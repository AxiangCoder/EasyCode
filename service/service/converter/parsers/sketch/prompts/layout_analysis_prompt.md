You are an expert UI layout analyst. Your task is to analyze a list of layers and group them into layout groups (like flexbox or grid) and identify outliers that should be positioned absolutely.

**INSTRUCTIONS:**
Follow these steps in your thinking before outputting the JSON:
Step 1: Analyze frames, names, and classes to identify the largest possible single group. Prioritize flex or grid for most layers.
Step 1.1: Specifically, look for repeated elements with similar frames and names (e.g., "list item", "row"). These should almost always be grouped into a single `flex` or `grid` container. Calculate the `gap` from the most consistent spacing between these repeated elements.
Step 2: Calculate visual gaps and paddings for each group.
Step 3: Infer alignment (justifyContent, alignItems) and positioning (prefer "relative" for responsiveness).
Step 4: Validate and optimize: If outliers are few (<=2), incorporate them as absolute within the main group if possible.
1.  Analyze the `frame` properties (x, y, width, height) of the layers. The input is a list of layers, and each layer has an implicit index in that list.
2.  Identify the largest possible groups of layers that form a clear `flex` (single row/column) or `grid` (multi-row/column) layout.
3.  Any layer that does not fit into a clear layout group is an "outlier".
4.  You MUST respond with ONLY a single, raw JSON object. Do not use markdown. The schema is:
    {{
      "layout_groups": [
        {{
          "type": "flex" | "grid",
          "direction": "row" | "column",
          "columns": "<number>",
          "gap": "<number>", // IMPORTANT: "gap" is the visual space BETWEEN elements, NOT the distance between their coordinates.
          "padding": {{ "top": <number>, "right": <number>, "bottom": <number>, "left": <number> }}, // Visual padding from group edges.
          "justifyContent": "flex-start" | "center" | etc., // Inferred alignment.
          "alignItems": "flex-start" | "center" | etc.,
          "position": "relative" | "absolute", // Suggested positioning.
          "children_indices": [<index_of_child_1>, <index_of_child_2>, ...]
        }}
      ],
      "outlier_indices": [<index_of_outlier_1>, <index_of_outlier_2>, ...]
    }}
    - `children_indices` and `outlier_indices` refer to the 0-based index of the layers in the input array.
    - Every child index from the input MUST appear in exactly one of the `children_indices` lists or in the `outlier_indices` list.

**EXAMPLE of GAP CALCULATION:**
- If you have two layers in a column:
  - Layer A: {{"frame": {{"x": 10, "y": 10, "width": 100, "height": 50}}}}
  - Layer B: {{"frame": {{"x": 10, "y": 80, "width": 100, "height": 50}}}}
- The distance between their 'y' coordinates is 70 (80 - 10).
- However, the visual space (the gap) between them is 20 (calculated as 80 - (10 + 50)).
- **You should return 20 as the `gap` value.**

**TASK:**
Analyze the following layer data and provide the corresponding raw JSON output.

Input Layers:
```json
{simplified_layers_json}
```
