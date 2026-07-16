/* Tech tree renderer for the homepage.
 *
 * Loaded on every page via mkdocs.yml extra_javascript, but only runs
 * when the #tech-tree container exists (i.e. on the homepage).
 * Reads docs/assets/graph.json produced by scripts/build_graph.py.
 */
(function () {
  "use strict";

  function init() {
    var container = document.getElementById("tech-tree");
    if (!container || typeof cytoscape === "undefined") return;

    // Category palette, one color per branch of the tree (Civ-style).
    // Keep in sync with the legend on the homepage.
    var styles = getComputedStyle(document.body);
    var categoryColors = {
      core: "#5c6bc0",          // indigo
      electronics: "#f9a825",   // amber
      mechanical: "#78909c",    // steel grey
      programming: "#43a047",   // green
      "data-science": "#8e24aa",// purple
      "ai-ml": "#e53935"        // red
    };
    var colors = {
      edge: styles.getPropertyValue("--md-default-fg-color--lighter").trim() || "#b0b0b0",
      label: "#ffffff",
      fallback: "#5c6bc0"
    };

    fetch(container.dataset.graphUrl || "assets/graph.json")
      .then(function (res) {
        if (!res.ok) throw new Error("graph.json not found (HTTP " + res.status + ")");
        return res.json();
      })
      .then(function (elements) {
        render(container, elements, colors, categoryColors);
      })
      .catch(function (err) {
        container.innerHTML =
          "<p>Could not load the tech tree: " + err.message + "</p>";
      });
  }

  function render(container, elements, colors, categoryColors) {
    var cy = cytoscape({
      container: container,
      elements: elements,
      autoungrabify: true, // nodes stay where dagre puts them
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "text-wrap": "wrap",
            "text-max-width": "120px",
            "font-size": "13px",
            "font-family": "var(--md-text-font-family, sans-serif)",
            color: colors.label,
            width: "label",
            height: "label",
            padding: "14px",
            shape: "round-rectangle",
            "background-color": function (node) {
              return categoryColors[node.data("category")] || colors.fallback;
            }
          }
        },
        {
          selector: "node[type = 'project']",
          style: {
            shape: "hexagon",
            padding: "20px",
            "border-width": 3,
            "border-color": "#ffffff"
          }
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": colors.edge,
            "target-arrow-color": colors.edge,
            "target-arrow-shape": "triangle",
            "curve-style": "bezier"
          }
        },
        {
          selector: ".highlighted",
          style: {
            "line-color": "#e53935",
            "target-arrow-color": "#e53935",
            width: 3
          }
        }
      ],
      layout: {
        name: "dagre",
        rankDir: "LR", // prerequisites on the left, advanced topics right
        nodeSep: 30,
        rankSep: 80,
        padding: 20
      },
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.1  // smoother zooming (lower = smoother)
    });

    // Click a node -> open its page. URLs in graph.json are relative
    // to the site root; since this only runs on the homepage (which IS
    // the site root), plain relative navigation resolves correctly.
    cy.on("tap", "node", function (evt) {
      window.location.href = evt.target.data("url");
    });

    // Hover: highlight the incoming prerequisite edges.
    cy.on("mouseover", "node", function (evt) {
      evt.target.incomers("edge").addClass("highlighted");
      container.style.cursor = "pointer";
    });
    cy.on("mouseout", "node", function (evt) {
      evt.target.incomers("edge").removeClass("highlighted");
      container.style.cursor = "default";
    });

    cy.fit(undefined, 30);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
