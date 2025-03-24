<script lang="ts">
    import * as d3 from 'd3';
    import { onMount } from 'svelte';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';

    // define opacity values
    const CIRCLE_OPACITIES = {STANDARD: 1, HOVER: 0.5};

    // Define interfaces for our data
    interface PlateData {
        plate_id: string;
        value: number;
        registration_state: string;
        violation_borough: string;
        fines: number;
    }

    interface HierarchyNode {
        name: string;
        value?: number;
        children?: HierarchyNode[];
        // Add additional properties for our data
        plate_id?: string;
        registration_state?: string;
        violation_borough?: string;
        fines?: number;
        group?: string;
    }

    // Props for the component
    let {
        dataPath = '/data/school_zone_violations_sparse.csv',
        width = 928,
        height = 928,
    } = $props();

    // References to DOM elements
    let container: HTMLElement;
    let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
    
    // Data processing function
    function processData(data: Array<Record<string, string>>): PlateData[] {
        // Filter out rows with missing values and convert to numbers
        const processedData = data
            .filter(d => d.plate_id && d.school_zone_violations)
            .map(d => ({
                plate_id: d.plate_id,
                value: +d.school_zone_violations,
                registration_state: d.registration_state,
                violation_borough: d.violation_borough,
                fines: +d.fines,
            }));
        
        // Sort by violation count in descending order
        return processedData.sort((a, b) => b.value - a.value);
    }
    
    // Function to create the circular packing visualization
    function createVisualization(data: PlateData[]): void {
        console.log("Creating visualization with", data.length, "items");
        
        // Clear any existing SVG
        d3.select(container).select("svg").remove();
        
        // Create the SVG container
        svg = d3.select(container)
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto;");
            
        // Create a hierarchical structure for the pack layout
        // Group data into 3 categories: 1 violation, 3-15 violations, 16+ violations
        const singleViolations = data.filter(d => d.value >= 1 && d.value <= 2);
        const mediumViolations = data.filter(d => d.value >= 3 && d.value <= 15);
        const highViolations = data.filter(d => d.value >= 16);
        
        // Create the hierarchical data structure
        const hierarchyData: HierarchyNode = {
            name: "All Violations",
            children: [
                {
                    name: "1-2 Violations",
                    group: "single",
                    children: singleViolations.map(d => ({
                        name: d.plate_id,
                        value: d.value,
                        plate_id: d.plate_id,
                        registration_state: d.registration_state,
                        violation_borough: d.violation_borough,
                        fines: d.fines,
                        group: "single"
                    }))
                },
                {
                    name: "3-15 Violations",
                    group: "medium",
                    children: mediumViolations.map(d => ({
                        name: d.plate_id,
                        value: d.value,
                        plate_id: d.plate_id,
                        registration_state: d.registration_state,
                        violation_borough: d.violation_borough,
                        fines: d.fines,
                        group: "medium"
                    }))
                },
                {
                    name: "16+ Violations",
                    group: "high",
                    children: highViolations.map(d => ({
                        name: d.plate_id,
                        value: d.value,
                        plate_id: d.plate_id,
                        registration_state: d.registration_state,
                        violation_borough: d.violation_borough,
                        fines: d.fines,
                        group: "high"
                    }))
                }
            ]
        };
        
        // Create the pack layout
        const pack = d3.pack<HierarchyNode>()
            .size([width - 40, height - 60])
            .padding(3);
            
        // Generate the hierarchy and calculate positions
        const root = d3.hierarchy<HierarchyNode>(hierarchyData)
            .sum(d => d.children ? 0 : d.value || 0) // Only leaf nodes contribute to size
            .sort((a, b) => (b.value || 0) - (a.value || 0));
            
        // Apply the pack layout
        const nodes = pack(root).descendants(); // Include all nodes now
        
        // Filter out the root node for rendering
        const displayNodes = nodes.filter(d => d.depth > 0);
        
        // Create a color scale for the groups
        const colorScale = d3.scaleOrdinal<string, string>()
            .domain(["single", "medium", "high"])
            .range(["var(--primary-blue)", "var(--primary-blue)", "var(--primary-blue)"]);
        
        // Create a group for all the circles and center it
        const g = svg.append("g")
            .attr("transform", `translate(20, 50)`);
            
        // Create the circles
        const circles = g.selectAll("circle")
            .data(displayNodes) // Use filtered nodes without the root
            .join("circle")
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("r", d => d.r)
            .attr("class", d => {
                // Apply different classes based on depth
                if (d.depth === 1) return "group-circle";
                return "leaf-circle";
            })
            .on("mouseover", function(event: MouseEvent, d: d3.HierarchyCircularNode<HierarchyNode>) {
                // Only apply hover effects for leaf nodes (individual plates)
                if (d.depth === 2) {
                    d3.select(this)
                        .classed("leaf-circle-hover", true);
                        
                    // Create or update tooltip
                    const tooltip = d3.select(container)
                        .selectAll(".tooltip")
                        .data([null])
                        .join("div")
                        .attr("class", "tooltip")
                    
                    // Get container's bounding rectangle to adjust coordinates properly
                    const containerRect = container.getBoundingClientRect();
                    // Calculate position relative to the container
                    const relativeX = event.clientX - containerRect.left;
                    const relativeY = event.clientY - containerRect.top;
                    
                    const tooltipContent = `
                        <strong>Plate ID:</strong> ${d.data.plate_id || d.data.name}<br>
                        <strong>Registration state:</strong> ${d.data.registration_state || 'N/A'}<br>
                        <strong>Main borough:</strong> ${d.data.violation_borough || 'N/A'}<br>
                        <strong>School zone violations:</strong> ${d.data.value || 0}<br>
                        <strong>Total fines:</strong> $${(d.data.fines || 0).toLocaleString()}
                    `;
                        
                    tooltip
                        .html(tooltipContent)
                        .style("left", `${relativeX + 15}px`) // position tooltip relative to container
                        .style("top", `${relativeY - 40}px`)  // position tooltip above the mouse
                        .style("opacity", 1);
                }
            })
            .on("mouseout", function() {
                const d = d3.select(this).datum() as d3.HierarchyCircularNode<HierarchyNode>;
                
                // Only reset styles for leaf nodes
                if (d.depth === 2) {
                    d3.select(this)
                        .classed("leaf-circle-hover", false);
                        
                    d3.select(container)
                        .selectAll(".tooltip")
                        .style("opacity", 0);
                }
            })
            .on("mousemove", function(event: MouseEvent) {
                const d = d3.select(this).datum() as d3.HierarchyCircularNode<HierarchyNode>;
                
                // Only update tooltip position for leaf nodes
                if (d.depth === 2) {
                    // Get container's bounding rectangle to adjust coordinates properly
                    const containerRect = container.getBoundingClientRect();
                    // Calculate position relative to the container
                    const relativeX = event.clientX - containerRect.left;
                    const relativeY = event.clientY - containerRect.top;
                    
                    d3.select(container)
                        .selectAll(".tooltip")
                        .style("left", `${relativeX + 15}px`) // keep tooltip relative to container
                        .style("top", `${relativeY - 40}px`); // keep tooltip above the mouse
                }
            });
            
        // Add group labels with text-fitted highlights
        // First, create a group for each label to contain both the highlight and text
        const labelGroups = g.selectAll("g.label-group")
            .data(displayNodes.filter(d => d.depth === 1))
            .join("g")
            .attr("class", "label-group")
            .attr("transform", d => `translate(${d.x}, ${d.y})`);

        // Add the text elements first (so we can measure them)
        const textElements = labelGroups.append("text")
            .attr("class", "group-label")
            .attr("x", 0)
            .attr("y", 0)
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .attr("font-size", d => Math.min(d.r / 3, 16))
            .attr("pointer-events", "none")
            .text(d => d.data.name);
            
        // Now measure each text element and add a highlight background behind it
        textElements.each(function(d, i) {
            const textElement = d3.select(this);
            const textNode = textElement.node() as SVGTextElement;
            const textWidth = textNode.getComputedTextLength();
            
            // Add a highlight rectangle that fits the text exactly
            // Get the parent group using the parent node element (safely check if it exists)
            const parentNode = this.parentNode;
            if (parentNode) {
                const parentGroup = d3.select(parentNode as SVGGElement);
                parentGroup.insert("rect", "text") // Insert before the text (so it's behind)
                    .attr("class", "label-background")
                    .attr("x", -textWidth/2 - 10) // Center with padding
                    .attr("y", -10) // Position with padding
                    .attr("width", textWidth + 20) // Add padding
                    .attr("height", 20) // Fixed height with padding
                    .attr("rx", 4) // Rounded corners
                    .attr("ry", 4);
            }
        });
    }
    
    // Handle window resize
    function handleResize(): void {
        // Only re-render if we have data loaded
        if (svg) {
            // Adjust SVG dimensions if needed
            svg.attr("width", width)
               .attr("height", height);
        }
    }
    
    onMount(() => {
        // Add resize event listener
        window.addEventListener('resize', handleResize);
        
        // Use our utility function to handle the path from props
        const fullDataPath = getFullPath(dataPath);
        console.log(`Loading data from: ${fullDataPath}`);
        
        // Load and process the data
        d3.csv(fullDataPath)
            .then(processData)
            .then(createVisualization)
            .catch((error: any) => {
                console.error("Error loading CSV:", error);
            });
            
        // Clean up event listeners on component destruction
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    });
</script>

<div class="circle-pack-container" bind:this={container}>
    <!-- The visualization will be rendered here -->
</div>

<style>
    .circle-pack-container {
        width: 100%;
        height: 100%;
        min-height: 500px;
        position: relative;
    }
    
    :global(.tooltip) {
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 14px;
        font-family: 'Helvetica', sans-serif;
        text-align: left;
        position: absolute;
        background-color: var(--color-background);
        color: black;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.25);
        border: 0px solid black;
        padding: 5px;
        pointer-events: all;
        font-weight: 300;
    }
    
    :global(.tooltip.visible) {
        opacity: 1;
    }

    :global(strong) {
        font-weight: 450;
    }
    
    :global(circle) {
        transition: opacity 0.3s, fill 0.3s, stroke-width 0.3s;
        cursor: pointer;
    }
    
    :global(.group-circle) {
        fill: var(--color-background);
        opacity: 1;
        stroke: black;
        stroke-width: 1px;
        stroke-dasharray: 5, 3;  /* Creates a dashed line pattern: 5px dash, 3px gap */
    }
    
    :global(.leaf-circle) {
        fill: var(--primary-blue);
        opacity: 1;
        stroke: none;
        stroke-width: 0;
    }
    
    :global(.leaf-circle-hover) {
        fill: #182E6F;
        stroke: black;
        stroke-width: 2px;
    }
    
    :global(.label-background) {
        fill: #31C9DE;
        opacity: 0.9;
        rx: 5px;
        ry: 5px;
    }
    
    :global(.group-label) {
        fill: black;
        font-weight: 500; 
        font-size: 20px;
        /* Remove text shadow and stroke since we have a background now */
        text-shadow: none;
        stroke: none;
    }
</style>

