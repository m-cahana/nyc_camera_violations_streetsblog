<script>
    import * as d3 from 'd3';
    import { onMount } from 'svelte';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';

    // define global variables
    let nodes = [];
    let simulation = null;
    let nodeHighlight = false;

    // Props for the component
    let {
        dataPath = '/data/school_zone_violations_sparse.csv',
        width = 1200,
        height = 1000,
        // Add scrolly content for sections
        scrollSections = [
            {
                title: "",
                content: "Each circle here represents a driver caught by school zone speed cameras at least once. Circles are sized based on the driver's violation count; the more violations the driver committed, the larger the circle."
            },
            {
                title: "Typical Offenders",
                content: "The typical offender will only speed through a school zone once a year."
            },
            {
                title: "Routine Offenders",
                content: "Drivers with 3-15 violations show a more consistent pattern of disregard for school zone safety. They're a large minority, and account for most violations."
            },
            {
                title: "Extreme Offenders",
                content: "Drivers with 16+ violations represent the top 1% of offenders. They account for a disproportionately large share of all violations, and post the greatest threat to public safety."
            },
            {
                title: "A Closer Look",
                content: "Let's visualize what it means when a single driver accumulates 20 violations - equivalent to 20 separate instances of endangering children in school zones."
            },
            {
                title: "The Most Dangerous Driver",
                content: "The most egregious offender in our dataset was caught speeding in school zones 755 times. That's more than twice every day of the school year, consistently endangering children's lives."
            }
        ]
    } = $props();

    // References to DOM elements
    let container;
    let svg;
    
    // Scrolly state
    let currentSection = $state(0);
    
    // Data processing function
    function processData(data) {
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
                row_pct: +d.row_pct
            }));
        
        // Sort by violation count in descending order
        return processedData.sort((a, b) => b.value - a.value);
    }
    
    // Function to create the circular packing visualization
    function createVisualization(data) {
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

            
        // Create nodes for the force simulation
        nodes = data.map(d => {
            // Create a scale for y position based on violations
            const yScale = d3.scaleLog()
                .domain([d3.min(data, d => d.value), d3.max(data, d => d.value)])
                .range([height * 0.4, height * 0.6]);  
                
            return {
                id: d.plate_id,
                value: d.value,
                plate_id: d.plate_id,
                registration_state: d.registration_state,
                violation_borough: d.violation_borough,
                fines: d.fines,
                violations: d.value,
                // square root of radius to ensure area is proportional to violations
                radius: Math.sqrt(d.value) * 3,
                // Initialize x coordinate randomly, y based on violations
                x: Math.random() * width,
                y: yScale(d.value),
                // Store target y for force
                targetY: yScale(d.value),
                closerLook: false
            };
        });
        
        // Create the force simulation
        simulation = d3.forceSimulation(nodes)
            .force("charge", d3.forceManyBody().strength(-3))
            .force("collision", d3.forceCollide().radius(d => d.radius * 0.9))
            .force("x", d3.forceX(d => d.x).strength(0.2))
            .force("y", d3.forceY(d => d.y).strength(.05));
            
        // Create a group for all the circles
        const g = svg.append("g")
            .attr("class", "circle-pack-group");
            
        // Create the circles
        const circles = g.selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "leaf-circle")
            .attr("r", d => d.radius)
            .on("mouseover", function(event, d) {
                d3.select(this)
                    .classed("leaf-circle-hover", true);
                    
                // Create or update tooltip
                const tooltip = d3.select(container)
                    .selectAll(".tooltip")
                    .data([null])
                    .join("div")
                    .attr("class", "tooltip")
                
                const tooltipContent = `
                    <strong>Plate ID:</strong> ${d.plate_id}<br>
                    <strong>Registration state:</strong> ${d.registration_state || 'N/A'}<br>
                    <strong>Main borough:</strong> ${d.violation_borough || 'N/A'}<br>
                    <strong>School zone violations:</strong> ${d.value}<br>
                    <strong>Total fines:</strong> $${(d.fines || 0).toLocaleString()}
                `;
                    
                tooltip
                    .html(tooltipContent)
                    .style("left", `${event.clientX + 15}px`)
                    .style("top", `${event.clientY - 40}px`)
                    .style("opacity", 1);
            })
            .on("mouseout", function() {
                d3.select(this)
                    .classed("leaf-circle-hover", false);
                    
                d3.select(container)
                    .selectAll(".tooltip")
                    .style("opacity", 0);
            })
            .on("mousemove", function(event) {
                d3.select(container)
                    .selectAll(".tooltip")
                    .style("left", `${event.clientX + 15}px`)
                    .style("top", `${event.clientY - 40}px`);
            });
            
        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
    }
    
    // Handle window resize
    function handleResize() {
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

    function resetNodes() {
        nodeHighlight = false;
        // Reset all node properties
        nodes.forEach(d => {
            d.closerLook = false;
            // Reset to original x and y positions
            d.x = Math.random() * width;
            d.y = d.targetY; // Use the stored target Y position
            // Remove highlight positions and scaling
            delete d.highlightX;
            delete d.highlightY;
            delete d.highlightRadius;
            delete d.opacity;
        });

        // Reset nodeHighlight flag
        nodeHighlight = false;

        // Restart simulation with original forces but stronger parameters for faster transition
        simulation
            .force("charge", d3.forceManyBody().strength(-10)) // Stronger repulsion
            .force("collision", d3.forceCollide().radius(d => d.radius * 0.9).strength(1)) // Stronger collision
            .force("x", d3.forceX(d => d.x).strength(0.5)) // Stronger x-positioning
            .force("y", d3.forceY(d => d.targetY).strength(0.2)) // Stronger y-positioning
            .alpha(0.8) // Higher initial energy
            .alphaDecay(0) // Faster decay rate
            .restart();
            
        // Reset circle sizes and opacity
        svg.selectAll(".leaf-circle")
            .style("fill-opacity", 1)
            .attr("r", d => d.radius);
    }

    function HighlightNodes(nodes, largerViolations, smallerViolations, scale = 1) {
        nodeHighlight = true;
        // Find a node with exactly largerViolations violations
        const targetNode = nodes.find(d => d.violations === largerViolations);
                
        if (targetNode && simulation) {
            // Center position in SVG
            const centerX = width / 2;
            const centerY = height / 2;
            
            // Reset all closerLook flags
            nodes.forEach(d => d.closerLook = false);
            
            // Move and style the target node
            targetNode.closerLook = true;
            targetNode.highlightX = centerX;
            targetNode.highlightY = centerY;
            targetNode.opacity = 0.2;
            targetNode.highlightRadius = targetNode.radius * scale * 1.8; // Scale up the target node by an additional 1.8

            const smallerNodes = nodes.filter(d => d.violations === smallerViolations).slice(0, largerViolations);
            
            // Create hierarchy for smaller nodes
            const packData = {
                children: smallerNodes.map(d => ({
                    radius: d.radius * scale, // Scale up the smaller nodes
                    data: d
                }))
            };
            
            // Create hierarchy and pack layout
            const root = d3.hierarchy(packData)
                .sum(d => d.radius * d.radius * (0.9 + Math.random() * 0.2)); // Add slight randomness to sizing
            
            const pack = d3.pack()
                .size([targetNode.highlightRadius * 1.8, targetNode.highlightRadius * 1.8])
                .padding(0.5 + Math.random() * 1); // Randomize padding between circles
            
            // Apply the pack layout
            pack(root);
            
            // Update positions of smaller nodes based on pack layout
            root.children.forEach((node, i) => {
                const originalNode = node.data.data;
                originalNode.closerLook = true;
                originalNode.highlightRadius = originalNode.radius * scale; // Store scaled radius
                // Add slight random offset to each node's position
                const randomAngle = Math.random() * Math.PI * 2;
                const randomRadius = Math.random() * 10;
                const randomX = Math.cos(randomAngle) * randomRadius;
                const randomY = Math.sin(randomAngle) * randomRadius;
                // Translate packed coordinates relative to target node center
                originalNode.highlightX = centerX + (node.x - targetNode.highlightRadius * 0.9) + randomX;
                originalNode.highlightY = centerY + (node.y - targetNode.highlightRadius * 0.9) + randomY;
            });

            // Move remaining nodes far away
            nodes.filter(d => !d.closerLook).forEach(node => {
                node.highlightX = 2000;
                node.highlightY = 2000;
            });

            // Restart simulation with modified forces
            simulation
                .force("charge", d3.forceManyBody().strength(-10))
                .force("x", d3.forceX(d => d.highlightX).strength(1))
                .force("y", d3.forceY(d => d.highlightY).strength(1))
                .force("collision", d3.forceCollide().radius(d => {
                    // Only apply collision radius to smaller nodes
                    // The larger node (targetNode) should not have collision detection
                    if (d === targetNode) return 0;  // No collision for the large node
                    return d.closerLook ? d.highlightRadius : d.radius;
                }).strength(1)) // Stronger collision force to prevent overlap
                .alpha(1)
                .alphaDecay(0.1) // Slower decay for more stable positioning
                .velocityDecay(0.6) // Add velocity decay to dampen movement
                .restart();
        }

        // Update circle sizes and colors
        svg.selectAll(".leaf-circle")
            .style("fill-opacity", d => d.opacity)
            .attr("r", d => d.closerLook ? d.highlightRadius : d.radius);
    }
    
    // Function to highlight groups based on current scroll section
    function updateVisualizationHighlights() {
        if (!svg) return;
        
        // Reset all highlights and positions
        svg.selectAll(".leaf-circle")
            .classed("dimmed", false)
            .transition()
            .attr("transform", "translate(0,0)");
            
        // Apply specific highlights based on the current section
        if (currentSection === 0) {
            // No highlighting or dimming for the initial overview section
            // All circles remain at full opacity
        } else if (currentSection === 1) {
            // Highlight single violations
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations > 1)
                .classed("dimmed", true);
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations == 1)
                .classed("dimmed", false);
            if (nodeHighlight) {
                resetNodes();
            } 
        } else if (currentSection === 2) {
            // Highlight medium violations (2-15)
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations >= 2 && d.violations < 15)
                .classed("dimmed", false);
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations < 2 || d.violations > 15)
                .classed("dimmed", true);
            if (nodeHighlight) {
                resetNodes();
            } 
        } else if (currentSection === 3) {
            // update circles with violations > 15
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations > 15)
                .classed("dimmed", false);
            svg.selectAll(".leaf-circle")
                .filter(d => d.violations <= 15)
                .classed("dimmed", true);
            if (nodeHighlight) {
                resetNodes();
            } 
        } else if (currentSection === 4) {
            HighlightNodes(nodes, 20, 1, 5); // Scale up by 5x for better visibility
        } else if (currentSection === 5) {
            HighlightNodes(nodes, 755, 1, 2); // Scale up by 8x for better visibility of the comparison
        }
    }
    
    // Effect to update visualization when section changes
    $effect(() => {
        if (currentSection !== undefined) {
            updateVisualizationHighlights();
        }
    });

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
            .catch((error) => {
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
                    {#if section.title !== ""}<h3>{section.title}</h3>{/if}
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
        z-index: 2;
        pointer-events: none; /* Make step transparent to mouse events */
    }
    
    .step-content {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 20px;
        max-width: 350px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-right: 5%;
        pointer-events: auto; /* Re-enable mouse events for the content box */
    }
    
    .step-content h3 {
		margin-top: 0;
		margin-bottom: 0.5em;
		font-weight: 550;
		font-size: 18px;
	}
	
	.step-content p {
		margin: 0;
        font-size: 16px;
        text-align: left;
	}
    
    /* Tooltip styles */
    :global(.tooltip) {
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 14px;
        font-family: 'Helvetica', sans-serif;
        text-align: left;
        position: fixed;
        background-color: white;
        color: black;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.25);
        border: 1px solid rgba(0,0,0,0.1);
        padding: 10px;
        pointer-events: none;
        font-weight: 300;
        z-index: 9999; /* Ensure tooltip is always on top */
        min-width: 200px;
        max-width: 300px;
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

    
    :global(.dimmed) {
        opacity: 0.2;
    }
    
    /* Label background styles - replace the generic label-background */
    :global(.label-background-line-1),
    :global(.label-background-line-2), 
    :global(.label-background-line-3) {
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
        font-size: 20px;
        font-family: 'Helvetica', sans-serif;
    }
    
    :global(.label-line-2), 
    :global(.label-line-3) {
        font-weight: 400;
        font-size: 18px;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Ensure Scrolly component has proper z-index */
    :global(.scrolly-container) {
        position: relative;
        z-index: 2;
        pointer-events: none; /* Make container transparent to mouse events */
    }
</style>