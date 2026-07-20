---
id: kinematics
title: "Robot Kinematics"
type: topic
category: ai-ml
tree_icon: angle
prerequisites: [mechanical-fundamentals, python-basics]
---

# Robot Kinematics

Kinematics studies the motion (position, velocity, orientation) of robot manipulators **without** considering forces that cause it.

- **Forward kinematics (FK):** given the joint angles, where is the end effector (the gripper/tool tip)?
- **Inverse kinematics (IK):** given a target position/orientation for the end effector, what joint angles get you there?

FK is always solvable and deterministic, it's just matrix multiplication. IK is the hard problem: it can have zero, one, or infinitely many solutions.

## You can move on when you can...

- Calculate forward kinematics using DH parameters
- Solve inverse kinematics for robot arms
- Derive and code forward kinematics for a manipulator using DH parameters
- Explain the tradeoffs between rotation matrices, Euler angles, and quaternions, and why gimbal lock matters in practice
- Explain why IK can have zero, one, or infinitely many solutions for a given target
- Implement an analytical IK solution (where one exists) and a numerical/Jacobian-based fallback, including damped least squares near singularities
- Identify a robot's workspace boundary and explain what a kinematic singularity is, in both the boundary and interior sense
- Generate a smooth joint trajectory between two configurations using at least one of: quintic polynomial, trapezoidal velocity profile, minimum-jerk
- Name at least three production IK/kinematics libraries and what each is best suited for

## Coordinate frames and homogeneous transforms

Every link in a robot arm has its own coordinate frame. To know where the end effector is in the *world* frame, you chain together the transform from each joint to the next. A rigid-body transform between two 3D frames is described by a rotation matrix \(R \in SO(3)\) and a translation vector \(t \in \mathbb{R}^3\), packed into a single 4x4 **homogeneous transformation matrix**:

\[
T = \begin{bmatrix} R & t \\ 0^T & 1 \end{bmatrix} =
\begin{bmatrix}
r_{11} & r_{12} & r_{13} & t_x \\
r_{21} & r_{22} & r_{23} & t_y \\
r_{31} & r_{32} & r_{33} & t_z \\
0 & 0 & 0 & 1
\end{bmatrix}
\]

Chaining frames is matrix multiplication. The pose of the end effector in the world frame, for an \(n\)-joint arm, is:

\[
T_0^n = T_0^1 \, T_1^2 \, T_2^3 \cdots T_{n-1}^n
\]

### Representing rotation: matrices, Euler angles, quaternions

\(R \in SO(3)\) (a 3x3 orthonormal matrix, \(\det R = 1\)) is unambiguous but has 9 numbers for 3 degrees of freedom (redundant). 

| Representation | DOF | Pros | Cons |
|---|---|---|---|
| Rotation matrix | 9 (redundant) | No singularities, easy to compose (matrix multiply) | Memory-heavy, needs re-orthonormalization after repeated multiplication |
| Euler angles (roll-pitch-yaw) | 3 | Intuitive, human-readable | **Gimbal lock**: loses a DOF at certain orientations |
| Quaternion \(q = w + xi + yj + zk\) | 4 (unit-norm constrained) | No gimbal lock, smooth interpolation (SLERP), compact | Less intuitive, sign ambiguity (\(q\) and \(-q\) represent the same rotation) |

The one thing from this table to take away is to **never use raw Euler angles for control or interpolation on a real arm**

## Forward kinematics with Denavit-Hartenberg parameters

Manually writing a transform per joint gets messy fast, so manipulators are conventionally described using **Denavit-Hartenberg (DH) parameters** (Denavit & Hartenberg, 1955).

| Parameter | Symbol | Meaning |
|---|---|---|
| Link length | \(a_i\) | distance between joint axes \(i-1\) and \(i\), along their common perpendicular |
| Link twist | \(\alpha_i\) | angle between joint axes \(i-1\) and \(i\) |
| Link offset | \(d_i\) | distance along joint axis \(i-1\) to the common perpendicular |
| Joint angle | \(\theta_i\) | rotation about joint axis \(i-1\) — **this is your control input** for a revolute joint |

The standard DH transform from frame \(i-1\) to frame \(i\) is:

\[
T_{i-1}^{i} =
\begin{bmatrix}
\cos\theta_i & -\sin\theta_i \cos\alpha_i & \sin\theta_i \sin\alpha_i & a_i \cos\theta_i \\
\sin\theta_i & \cos\theta_i \cos\alpha_i & -\cos\theta_i \sin\alpha_i & a_i \sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}
\]

Multiplying these together for every joint gives FK for the whole arm, per the chained-transform equation above.

Given below is python implementation of the same for a 2-link planar arm.

```python
import numpy as np

def dh_transform(a, alpha, d, theta):
    """Standard DH transform for one joint."""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0,   sa,       ca,      d],
        [0,   0,        0,       1],
    ])

def forward_kinematics(dh_params, thetas):
    """General FK for any number of revolute joints.
    dh_params: list of (a, alpha, d) per joint (theta supplied separately
    since it's the variable joint angle).
    """
    T = np.eye(4)
    for (a, alpha, d), theta in zip(dh_params, thetas):
        T = T @ dh_transform(a, alpha, d, theta)
    return T

# 2-link planar arm: both links length 1, no twist/offset
dh_params = [(1.0, 0, 0), (1.0, 0, 0)]
T = forward_kinematics(dh_params, [np.radians(30), np.radians(45)])
x, y = T[0, 3], T[1, 3]
print(f"End effector at ({x:.3f}, {y:.3f})")
```

!!! tip "Sanity-check FK before you ever attempt IK"
    If your FK is wrong, your IK will fail in confusing ways that look like IK bugs but aren't. Verify FK against a case you can compute by hand (e.g. all joint angles at zero) before moving on.

## Velocity kinematics and the Jacobian

The **manipulator Jacobian** \(J(\theta) \in \mathbb{R}^{6 \times n}\) maps joint velocities to end-effector spatial velocity (linear + angular):

\[
\begin{bmatrix} \dot{p} \\ \omega \end{bmatrix} = J(\theta)\, \dot{\theta}
\]

For a planar 2-link arm (linear velocity only, \(2 \times 2\)):

\[
J(\theta) =
\begin{bmatrix}
-l_1 \sin\theta_1 - l_2 \sin(\theta_1+\theta_2) & -l_2 \sin(\theta_1+\theta_2) \\
l_1 \cos\theta_1 + l_2 \cos(\theta_1+\theta_2) & l_2 \cos(\theta_1+\theta_2)
\end{bmatrix}
\]

A **singularity** occurs where \(\det J = 0\),the arm momentarily loses a degree of freedom in task space, no matter how the joints move. This is why numerical IK solvers use the Moore-Penrose pseudo-inverse \(J^+\) rather than a true inverse: \(J^{-1}\) simply doesn't exist when \(J\) is rank-deficient, and even near a singularity \(J^{-1}\) blows up numerically.

## Inverse kinematics: analytical vs. numerical

**Analytical (closed-form), 2-link case.** Given target \((x, y)\), use the law of cosines to solve for \(\theta_2\) directly:

\[
\cos\theta_2 = \frac{x^2 + y^2 - l_1^2 - l_2^2}{2\, l_1 l_2}
\]

then back out \(\theta_1\) from the geometry. Note \(\theta_2 = \pm\arccos(\cdot)\) has **two valid solutions** , "elbow up" and "elbow down"

```python
def inverse_kinematics_2link(x, y, l1=1.0, l2=1.0, elbow_up=True):
    """Analytical IK for a 2-link planar arm."""
    d = np.sqrt(x**2 + y**2)
    if d > (l1 + l2) or d < abs(l1 - l2):
        raise ValueError("Target is outside the reachable workspace")

    cos_theta2 = (x**2 + y**2 - l1**2 - l2**2) / (2 * l1 * l2)
    sign = 1 if elbow_up else -1
    theta2 = sign * np.arccos(np.clip(cos_theta2, -1.0, 1.0))

    k1 = l1 + l2 * np.cos(theta2)
    k2 = l2 * np.sin(theta2)
    theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)

    return theta1, theta2
```

Real 6+ DOF arms rarely have a clean closed form like this. Three production-grade approaches:

**1. Numerical, Jacobian pseudo-inverse (Newton-Raphson style):**

```python
def inverse_kinematics_numerical(target_xy, theta_init, l1=1.0, l2=1.0,
                                   max_iters=200, tol=1e-4, alpha=0.5):
    """Jacobian pseudo-inverse IK."""
    theta = np.array(theta_init, dtype=float)

    for _ in range(max_iters):
        T = forward_kinematics([(l1, 0, 0), (l2, 0, 0)], theta)
        x, y = T[0, 3], T[1, 3]
        error = np.array(target_xy) - np.array([x, y])
        if np.linalg.norm(error) < tol:
            break

        J = np.array([
            [-l1*np.sin(theta[0]) - l2*np.sin(theta[0]+theta[1]),
             -l2*np.sin(theta[0]+theta[1])],
            [ l1*np.cos(theta[0]) + l2*np.cos(theta[0]+theta[1]),
              l2*np.cos(theta[0]+theta[1])],
        ])
        theta += alpha * np.linalg.pinv(J) @ error

    return theta
```

**2. Damped least squares (Levenberg-Marquardt), for robustness near singularities.** Plain pseudo-inverse still misbehaves close to a singularity (large joint velocity spikes). Adding a damping term \(\lambda\) trades a bit of tracking accuracy for stability:

\[
\dot{\theta} = J^T (J J^T + \lambda^2 I)^{-1} \dot{p}
\]

This is the technique behind most production IK solvers (KDL's `ChainIkSolverVel_wdls`, TRAC-IK's fallback mode).

**3. Closed-form solvers for real 6-DOF arms.** For arms with a spherical wrist (three intersecting final joint axes,true of most industrial and collaborative arms), the IK problem decouples into a solvable position sub-problem and orientation sub-problem, giving closed-form solutions even in 6D. **IKFast** (part of OpenRAVE, Diankov, 2010) auto-generates this closed-form C++ code per robot model , this is what most commercial arm vendors ship rather than relying purely on numerical solvers, because closed-form is faster and returns *all* valid solutions, not just the nearest local one.

## Workspace and singularities

- **Workspace** is the set of all reachable end-effector points. For the 2-link arm it's an annulus with outer radius \(l_1 + l_2\) and inner radius \(|l_1 - l_2|\) 
- **Singularities**: besides the Jacobian-rank definition above, it's useful to know two common categories ,**boundary singularities** (arm fully outstretched, at the edge of its workspace) and **interior singularities** (e.g. wrist joints aligning, common on 6-DOF arms with a spherical wrist). Both cause the same problemsolver needs very large joint velocities for a small commanded task-space motion.

!!! warning "Why this matters on real hardware"
    Commanding a real arm through a singularity can cause a sudden, large joint velocity spike as the solver tries to compensate. Production controllers clamp joint velocities and/or switch to damped least squares specifically to guard against this.

## Trajectory planning

FK/IK gets you *a* pose. Trajectory planning gets you a smooth path of poses **over time**.

**Quintic (5th-order) polynomial** : the simplest approach that gives zero velocity *and* acceleration at both endpoints:

\[
\theta(t) = \theta_0 + (\theta_f - \theta_0)\left(10s^3 - 15s^4 + 6s^5\right), \quad s = t / t_f
\]

```python
def quintic_trajectory(theta_start, theta_end, duration, t):
    """Position at time t along a smooth quintic trajectory."""
    s = np.clip(t / duration, 0, 1)
    blend = 10*s**3 - 15*s**4 + 6*s**5
    return theta_start + (theta_end - theta_start) * blend
```

**Trapezoidal velocity profile** : constant acceleration, constant cruise velocity, constant deceleration. More common on real industrial controllers because it's easy to reason about peak velocity/acceleration limits directly, at the cost of a discontinuous (but bounded) acceleration.

**Minimum-jerk trajectories** : used when smoothness of the *acceleration* itself matters (e.g. handling fragile payloads, or human-robot interaction where jerky motion feels unsafe); minimizes the integral of squared jerk over the trajectory.


## Libraries and implementations

You will very rarely hand-code IK for a real arm in production, the actual production libraries used are listed below: 

| Library | Language | What it's for |
|---|---|---|
| [Orocos KDL](https://github.com/orocos/orocos_kinematics_dynamics) | C++ (Python bindings) | The classic ROS/ROS 2 kinematics/dynamics library , Jacobian-based IK, widely used as MoveIt's default solver |
| [TRAC-IK](https://bitbucket.org/traclabs/trac_ik) | C++ (ROS wrapper) | Drop-in KDL replacement; runs Newton's method and SQP in parallel, generally faster and more reliable convergence than plain KDL |
| [IKFast (OpenRAVE)](https://openrave.org/docs/latest_stable/openravepy/ikfast/) | Generates C++ | Auto-generates closed-form analytical IK for arms with a spherical wrist , the gold standard for speed when applicable |
| [MoveIt 2](https://moveit.picknik.ai/) | C++/Python (ROS 2) | Full motion-planning stack , collision-aware IK, path planning, execution; wraps KDL/TRAC-IK/IKFast under the hood |
| [Pinocchio](https://github.com/stack-of-tasks/pinocchio) | C++/Python | Fast rigid-body dynamics + kinematics library, popular in research and legged robotics; strong autodiff support |
| [Drake](https://drake.mit.edu/) | C++/Python | MIT's model-based design toolkit , kinematics, dynamics, optimization-based control, simulation, all in one |
| [Peter Corke's Robotics Toolbox for Python](https://github.com/petercorke/robotics-toolbox-python) | Python | The best tool for *learning* , pure Python, readable, great for prototyping DH models and visualizing FK/IK before touching ROS |
| [ikpy](https://github.com/Phylliade/ikpy) | Python | Lightweight pure-Python IK from a URDF , good for quick scripts, less robust than KDL/TRAC-IK for production |

## References

- Denavit, J. & Hartenberg, R.S. (1955). *A kinematic notation for lower-pair mechanisms based on matrices.* Journal of Applied Mechanics.
- Foote, T. (2013). *tf: The transform library.* IEEE International Conference on Technologies for Practical Robot Applications (TePRA).
- Lynch, K. & Park, F. (2017). *Modern Robotics: Mechanics, Planning, and Control.* Cambridge University Press — the free companion site below is the best single reference for everything on this page.
- Diankov, R. (2010). *Automated Construction of Robotic Manipulation Programs.* PhD thesis, Carnegie Mellon University — the IKFast approach.
- Buss, S.R. (2004). *Introduction to Inverse Kinematics with Jacobian Transpose, Pseudoinverse and Damped Least Squares methods.* — the standard reference for the numerical IK methods above.

## External Resources

- [Modern Robotics - Coursera](https://www.coursera.org/specializations/modernrobotics)
- [Introduction to Robotics - Stanford](https://see.stanford.edu/Course/CS223A)
- [Peter Corke Robotics Toolbox](https://github.com/petercorke/robotics-toolbox-python)
- [MoveIt 2 Kinematics documentation](https://moveit.picknik.ai/main/doc/examples/kinematics/kinematics_tutorial.html)
- [Buss, Introduction to Inverse Kinematics (PDF)](https://www.math.ucsd.edu/~sbuss/ResearchWeb/ikmethods/iksurvey.pdf)
- [Modern Robotics: Mechanics, Planning, and Control (free textbook + video lectures)](https://hades.mech.northwestern.edu/index.php/Modern_Robotics)

