<script lang="ts">
    import * as d3 from 'd3';
    import { onMount } from 'svelte';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';


    // Define interfaces for our data
    interface PlateData {
        plate_id: string;
        value: number;
        registration_state: string;
        violation_borough: string;
        fines: number;
        cum_share: number;
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
        // Add scrolly content for sections
        scrollSections = [
            {
                title: "Minor Offenders (1-2 violations)",
                content: "Vehicles with 1-2 violations make up the majority of offenders. While these are minor offenders, they still contribute to unsafe conditions around schools."
            },
            {
                title: "Repeat Offenders (3-15 violations)",
                content: "These vehicles have between 3 and 15 violations, showing a pattern of disregard for school zone safety. They represent drivers who repeatedly break the law."
            },
            {
                title: "Extreme Offenders (16+ violations)",
                content: "The most dangerous vehicles have 16 or more violations. These extreme offenders pose a significant threat to children's safety in school zones."
            }
        ]
    } = $props();

    // References to DOM elements
    let container: HTMLElement;
    let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
    
    // Scrolly state
    let currentSection = $state(0);
    
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
                cum_share: +d.cum_share,
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

        // Create the hierarchical data structure with share info
        const hierarchyData: HierarchyNode = {
            name: "All Violations",
            children: [
                {
                    name: `1-2 Violations\n${(((d3.max(singleViolations, d => d.cum_share) ?? 0) - (d3.min(singleViolations, d => d.cum_share) ?? 0)) * 100).toFixed(0)}% of all violations`,
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
                    name: `3-15 Violations\n${(((d3.max(mediumViolations, d => d.cum_share) ?? 0) - (d3.min(mediumViolations, d => d.cum_share) ?? 0)) * 100).toFixed(0)}% of all violations`,
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
                    name: `16+ Violations\n${(((d3.max(highViolations, d => d.cum_share) ?? 0) - (d3.min(highViolations, d => d.cum_share) ?? 0)) * 100).toFixed(0)}% of all violations`,
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
            .size([width, height])
            .padding(3); // Scale padding proportionally
            
        // Generate the hierarchy and calculate positions
        const root = d3.hierarchy<HierarchyNode>(hierarchyData)
            .sum(d => d.children ? 0 : d.value || 0) // Only leaf nodes contribute to size
            .sort((a, b) => (b.value || 0) - (a.value || 0));
            
        // Apply the pack layout
        const nodes = pack(root).descendants(); // Include all nodes now
        
        // Filter out the root node for rendering
        const displayNodes = nodes.filter(d => d.depth > 0);
        
        // Create a group for all the circles and center it
        const g = svg.append("g")
            .attr("transform", `translate(${width/2}, ${height/2 - 100})`);
            
        // Create the circles
        const circles = g.selectAll("circle")
            .data(displayNodes) // Use filtered nodes without the root
            .join("circle")
            .attr("cx", d => d.x - width/2)
            .attr("cy", d => d.y - height/2)
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
            .attr("transform", d => `translate(${d.x - width/2}, ${d.y - height/2})`);

        // Add the text elements first (so we can measure them)
        const textElements = labelGroups.append("text")
            .attr("class", "group-label")
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle");
            
        // Add tspans for multi-line text with separate classes
        textElements.each(function(d) {
            const textElement = d3.select(this);
            const lines = d.data.name.split('\n');
            
            // Clear any existing content
            textElement.html("");
            
            // Add first line (title) with a specific class
            textElement.append("tspan")
                .attr("class", "label-line-1")
                .attr("x", 0)
                .attr("y", -12)
                .text(lines[0]);
            
            // Add second line (percentage) with a specific class
            textElement.append("tspan")
                .attr("class", "label-line-2")
                .attr("x", 0)
                .attr("y", 12)
                .text(lines[1]);
        });
            
        // Now create separate highlight rectangles for each line
        textElements.each(function(d) {
            const textElement = d3.select(this);
            const parentNode = this.parentNode;
            if (!parentNode) return;
            
            const parentGroup = d3.select(parentNode as SVGGElement);
            
            // Measure the first line (title)
            const firstLine = textElement.select(".label-line-1").node() as SVGTextElement;
            const firstLineWidth = firstLine.getComputedTextLength();
            
            // Create highlight for first line
            parentGroup.insert("rect", "text")
                .attr("class", "label-background-line-1")
                .attr("x", -firstLineWidth/2 - 10)
                .attr("y", -25)
                .attr("width", firstLineWidth + 20)
                .attr("height", 26);
                
            // Measure the second line (percentage)
            const secondLine = textElement.select(".label-line-2").node() as SVGTextElement;
            const secondLineWidth = secondLine.getComputedTextLength();
            
            // Create highlight for second line
            parentGroup.insert("rect", "text")
                .attr("class", "label-background-line-2")
                .attr("x", -secondLineWidth/2 - 10)
                .attr("y", 0)
                .attr("width", secondLineWidth + 20)
                .attr("height", 24);
        });
    }
    
    // Handle window resize
    function handleResize(): void {
        // Only re-render if we have data loaded
        if (svg) {
            // Adjust SVG dimensions if needed
            svg.attr("width", width)
               .attr("height", height);
               
            // Update the center point of the visualization
            svg.select(".circle-pack-group")
               .attr("transform", `translate(${width/2}, ${height/2 - 100})`);
        }
    }
    
    // Function to highlight groups based on current scroll section
    function updateVisualizationHighlights() {
        if (!svg) return;
        
        // Reset all highlights
        svg.selectAll(".group-circle")
            .classed("highlighted", false)
            .classed("dimmed", false);
        
        svg.selectAll(".leaf-circle")
            .classed("dimmed", false);
            
        // Apply specific highlights based on the current section
        if (currentSection === 0) {
            // Highlight single violations group
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group !== "single")
                .classed("dimmed", true);
                
            svg.selectAll(".leaf-circle")
                .filter((d: any) => d.data.group !== "single")
                .classed("dimmed", true);
                
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group === "single")
                .classed("highlighted", true);
        } else if (currentSection === 1) {
            // Highlight medium violations group
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group !== "medium")
                .classed("dimmed", true);
                
            svg.selectAll(".leaf-circle")
                .filter((d: any) => d.data.group !== "medium")
                .classed("dimmed", true);
                
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group === "medium")
                .classed("highlighted", true);
        } else if (currentSection === 2) {
            // Highlight high violations group
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group !== "high")
                .classed("dimmed", true);
                
            svg.selectAll(".leaf-circle")
                .filter((d: any) => d.data.group !== "high")
                .classed("dimmed", true);
                
            svg.selectAll(".group-circle")
                .filter((d: any) => d.data.group === "high")
                .classed("highlighted", true);
        }
    }
    
    // Effect to update visualization when section changes
    $effect(() => {
        if (currentSection !== undefined) {
            updateVisualizationHighlights();
        }
    });
    
    // Update scrollSections with percentage information after loading data
    function updateScrollSectionsWithPercentages(singleShare: number, mediumShare: number, highShare: number) {
        scrollSections = [
            {
                title: `Minor Offenders (1-2 violations)\n${singleShare.toFixed(1)}% of all violations`,
                content: `Vehicles with 1-2 violations make up ${singleShare.toFixed(1)}% of all violations. While these are minor offenders, they still contribute to unsafe conditions around schools.`
            },
            {
                title: "Repeat Offenders (3-15 violations)",
                content: "These vehicles have between 3 and 15 violations, showing a pattern of disregard for school zone safety. They represent drivers who repeatedly break the law."
            },
            {
                title: "Extreme Offenders (16+ violations)",
                content: "The most dangerous vehicles have 16 or more violations. These extreme offenders pose a significant threat to children's safety in school zones."
            }
        ];
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

<section id="scrolly">
    <!-- Background visualization container -->
    <div class="visualization-container" bind:this={container}>
        <!-- The visualization will be rendered here by D3 -->
    </div>
    
    <!-- Spacer to start scrolling below the initial view -->
    <div class="spacer"></div>
    
    <!-- Scrolly component for text sections -->
    <Scrolly bind:value={currentSection}>
        {#each scrollSections as section, i}
            <div class="step" class:active={currentSection === i}>
                <div class="step-content">
                    <h3>{section.title}</h3>
                    <p>{section.content}</p>
                </div>
            </div>
        {/each}
    </Scrolly>
    
    <!-- Spacer at the end to ensure we can scroll to the last section -->
    <div class="spacer"></div>
</section>

<style>
    #scrolly {
        position: relative;
        width: 100%;
    }
    
    .visualization-container {
        position: sticky;
        top: 0;
        height: 100vh;
        width: 100%;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden; /* Prevent any overflow issues */
    }
    
    /* SVG specific styles to ensure proper sizing and centering */
    :global(.visualization-container svg) {
        width: 100%;
        height: 100%;
        max-height: 100vh;
        display: block; /* Remove any baseline alignment issues */
    }
    
    /* Make sure the containing group is properly centered */
    :global(.circle-pack-group) {
        transform-origin: center center;
    }
    
    .spacer {
        height: 50vh;
    }
    
    .step {
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 0 20px;
        position: relative;
        z-index: 5;
    }
    
    .step-content {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 20px;
        max-width: 350px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-right: 5%;
        transition: opacity 0.3s, transform 0.3s;
    }
    
    .step-content h3 {
        margin-top: 0;
        margin-bottom: 0.5em;
        font-weight: 550;
        font-size: 18px;
        white-space: pre-line; /* Handle line breaks in the title */
    }
    
    /* Style the second line (percentage line) of the section titles */
    .step-content h3::after {
        content: "";
        display: block;
        font-weight: 400;
        font-size: 16px;
        margin-top: 2px;
    }
    
    .step-content p {
        margin: 0;
        font-weight: 300;
    }
    
    /* Tooltip styles */
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
        z-index: 10;
    }
    
    :global(strong) {
        font-weight: 450;
    }
    
    /* Circle styles */
    :global(circle) {
        transition: opacity 0.5s, fill 0.5s, stroke-width 0.3s;
        cursor: pointer;
    }
    
    :global(.group-circle) {
        fill: var(--color-background);
        opacity: 1;
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
    
    /* New highlight styles for scrolly interaction */
    :global(.highlighted) {
        stroke: #31C9DE;
        stroke-width: 4px;
    }
    
    :global(.dimmed) {
        opacity: 0.2;
    }
    
    /* Label background styles - replace the generic label-background */
    :global(.label-background-line-1),
    :global(.label-background-line-2) {
        fill: #31C9DE;
        opacity: 0.9;
        rx: 5px;
        ry: 5px;
    }
    
    /* Group label base styles */
    :global(.group-label) {
        fill: black;
        font-weight: 500; 
        font-size: 20px;
        text-shadow: none;
        stroke: none;
    }
    
    /* Specific styles for each line */
    :global(.label-line-1) {
        font-weight: 600;
        font-style: italic;
        font-size: 20px;
        font-family: 'Helvetica', sans-serif;
    }
    
    :global(.label-line-2) {
        font-weight: 400;
        font-size: 18px;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Media query for responsive label size */
    @media (max-width: 768px) {
        :global(.group-label) {
            font-size: 16px;
        }
        
        :global(.label-line-2) {
            font-size: 14px;
        }
    }
    
    /* Ensure Scrolly component has proper z-index */
    :global(.scrolly-container) {
        position: relative;
        z-index: 10;
    }
</style>