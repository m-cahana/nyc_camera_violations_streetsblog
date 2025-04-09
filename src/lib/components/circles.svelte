<script>
    import * as d3 from 'd3';
    import { onMount } from 'svelte';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';

    // define global variables
    let nodes = [];
    let simulation = null;
    let circles = null;
    let nodeHighlight = false;
    let nodePositionChanged = false;

    // Props for the component
    let {
        dataPath = '/data/school_zone_violations_sparse.csv',
        width = 1200,
        height = 1000,
        // Add scrolly content for sections
        scrollSections = [
            {
                title: "",
                content: "Looking at this sample, which circles draw your attention? "
            },
            {
                title: "",
                content: "Probably these large ones. Each represents a driver with 15+ violations. These drivers can be considered <span class = 'extreme-offender'>extreme offenders</span>."
            },
            {
                title: "", 
                content: `However these extreme offenders are pretty rare; fewer than 1% of offenders commit 15+ violations. The <span class = 'typical-offender'>typical offender</span> actually only commits 1 violation a year.`
            },
            {
                title: "",
                content: "<span class = 'extreme-offender'>Extreme offenders</span> are important for the same reason they capture visual attention: despite being small in number, they have an oversized impact on school zone violations. Let's look at how they compare to the <span class = 'typical-offender'>typical offender</span>."
            },
            {
                title: "", 
                content: "An <span class = 'extreme-offender'>extreme offender</span> commits <span class = 'highlight-text'>19 violations a year on average</span>. Meaning one extreme offender poses as much danger as 19 <span class = 'typical-offender'>typical offenders</span>."
            },
            {
                title: "",
                content: "And in some cases, the disparity is way larger. Last year's <span class = 'extreme-offender'>most extreme offender</span> was caught speeding in school zones <span class = 'highlight-text'>545 times</span>. That's roughly one and a half times a day on average. "
            }
        ]
    } = $props();

    // References to DOM elements
    let container;
    let svg;
    
    // Scrolly state
    let currentSection = $state(0);
    let previousSection = 0; // Track the previous section
    
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

    function randomNumberBetween(min, max) {
        return Math.random() * (max - min) + min;
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
                .range([height * 0.1, height * 0.8]);  
                
            // For nodes with 545 violations, constrain their position 
            let xPos, yPos;
            if (d.value === 545) {
                xPos = randomNumberBetween(0.1, 0.9) * width;
                yPos = randomNumberBetween(0.1, 0.9) * height;
            } else {
                xPos = Math.random() * width;
                yPos = Math.random() * height;
            }
                
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
                x: xPos,
                y: yPos,
                xOriginal: xPos,
                yOriginal: yPos,
                // Store target y for force
                targetY: yScale(d.value),
                closerLook: false
            };
        });
        
        // Create the force simulation
        simulation = d3.forceSimulation(nodes)
            .force("collision", d3.forceCollide().radius(d => d.radius * 1.1).strength(1.8))
            
        // Create a group for all the circles
        const g = svg.append("g")
            .attr("class", "circle-pack-group");
            
        // Create the circles
        circles = g.selectAll("circle")
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

    
    function resetNodePosition(simulation, circles) {
        console.log('resetting node positions')
        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .transition()
                .ease(d3.easeLinear) // Smooth easing function
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
          
    }

    function pareBackNodes(nodes, circles, violationExamples = [545, 19]) {

        let counter = 0;
        nodes.filter(d => d.violations === violationExamples[0]).forEach(
            node => {
                if (counter >= 1) {
                    node.highlightX = 2000;
                    node.highlightY = 2000;
                }
                else {
                    node.highlightX = 0.5 * width;
                    node.highlightY = 0.3 * height;
                    node.furtherSqueeze = true;
                }
                counter++;
            }
        );

        counter = 0;
        nodes.filter(d => d.violations === violationExamples[1]).forEach(
            node => {
                if (counter >= 1) {
                    node.highlightX = 2000;
                    node.highlightY = 2000;
                }
                // force us to show specific example
                else if (node.plate_id === 'HSU6447') {
                    node.highlightX = 0.5 * width;
                    node.highlightY = 0.45 * height;
                    node.furtherPareBack = true;
                }
                counter++;
            }
        );

        nodes.filter(d => d.violations !== violationExamples[0] && d.violations !== violationExamples[1] && d.violations !== 1).forEach(
            node => {
                node.highlightX = 2000;
                node.highlightY = 2000;
            }
        );

        counter = 0;
        nodes.filter(d => d.violations === 1).forEach(
            node => {
                if (counter >= violationExamples[0] + violationExamples[1]) {
                    node.highlightX = 2000;
                    node.highlightY = 2000;
                }
                else {
                    // Position nodes to fill the interior of a circle
                    let centerX, centerY, maxRadius;
                    
                    if (counter < violationExamples[0]) {
                        centerX = 0.5 * width;
                        centerY = 0.7 * height;
                        maxRadius = 0.0725 * Math.min(width, height);
                        node.furtherSqueeze = true;
                    } else {
                        centerX = 0.5 * width;
                        centerY = 0.55 * height;
                        maxRadius = 0.01 * Math.min(width, height);
                        node.furtherPareBack = true;
                    }
                    
                    // Calculate a random radius between 0 and maxRadius
                    const radius = Math.sqrt(Math.random()) * maxRadius;
                    
                    // Calculate a random angle
                    const angle = Math.random() * 2 * Math.PI;
                    
                    // Calculate position within the circle
                    node.highlightX = centerX + radius * Math.cos(angle);
                    node.highlightY = centerY + radius * Math.sin(angle);
                } 
                counter++;
            }
        );

        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .transition()
                .ease(d3.easeLinear) // Smooth easing function
                .attr("cx", d => d.highlightX)
                .attr("cy", d => d.highlightY);
        });
    }

    function pareBackNodesFurther(nodes, circles) {
        nodes.filter(d => d.furtherPareBack).forEach(
            node => {
                node.highlightX = 2000;
                node.highlightY = 2000;
            }
        );

        nodes.filter(d => d.furtherSqueeze).forEach(
            node => {
                if (node.highlightY == 0.3 * height) {
                    node.highlightY = 0.4 * height
                } else {
                    node.highlightY = node.highlightY - 0.05 * height
                }
            }
        );

        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .transition()
                .ease(d3.easeLinear) // Smooth easing function
                .attr("cx", d => d.highlightX)
                .attr("cy", d => d.highlightY);
        });
    }


    function simulationTickReset(simulation, nodes, circles) {
        console.log('resetting simulation')
        

        nodes.forEach(node => {
            node.x = node.xOriginal;
            node.y = node.yOriginal;
        });

        simulation.on("tick", () => {
            circles
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
    }

    function resetNodeOpacityRadius(svg) {
        svg.selectAll(".leaf-circle")
            .style("fill-opacity", 1)
            .attr("r", d => d.radius);
    }


    function dimNodes(svg, violationsMin, violationsMax) {
         svg.selectAll(".leaf-circle")
                .filter(d => d.violations >= violationsMin && d.violations <= violationsMax)
                .classed("dimmed", false);
        svg.selectAll(".leaf-circle")
            .filter(d => d.violations < violationsMin || d.violations > violationsMax)
            .classed("dimmed", true);
    }
    
    function zoomIn(svg, nodes, circles, zoomTop = 0.4, zoomBottom = 0.6, zoomFactor = 5.2) {
        // Define the zoom area (middle 20% of the height)
        const zoomAreaTop = zoomTop * height;
        const zoomAreaBottom = zoomBottom * height;
        const zoomAreaHeight = zoomAreaBottom - zoomAreaTop;
        
        // Calculate the new viewBox dimensions
        const newViewBoxHeight = height / zoomFactor;
        const newViewBoxWidth = width / zoomFactor;
        
        // Calculate the center point of the zoom area
        const zoomCenterY = (zoomAreaTop + zoomAreaBottom) / 2;
        const zoomCenterX = width / 2;
        
        // Calculate the new viewBox position to center on the zoom area
        const newViewBoxX = zoomCenterX - newViewBoxWidth / 2;
        const newViewBoxY = zoomCenterY - newViewBoxHeight / 2;
        
        // Apply the zoom transformation to the SVG
        svg.transition()
            .duration(1000) // 1 second transition
            .ease(d3.easeCubicInOut)
            .attr("viewBox", `${newViewBoxX} ${newViewBoxY} ${newViewBoxWidth} ${newViewBoxHeight}`);
            
        // Update the simulation to focus on nodes in the zoom area
        simulation
            .force("x", d3.forceX(zoomCenterX).strength(0.1))
            .force("y", d3.forceY(zoomCenterY).strength(0.1))
            .alpha(0.3)
            .restart();
            
        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .transition()
                .ease(d3.easeLinear)
                .attr("cx", d => d.highlightX)
                .attr("cy", d => d.highlightY);
        });
    }
    
    function zoomReset(svg, nodes, circles) {
        // Reset the viewBox to show the entire visualization
        svg.transition()
            .duration(1000) // 1 second transition
            .ease(d3.easeCubicInOut)
            .attr("viewBox", `0 0 ${width} ${height}`);
            
        // Remove the zoom forces from the simulation
        simulation
            .force("x", null)
            .force("y", null)
            .alpha(0.3)
            .restart();
            
        // Update circle positions on each tick
        simulation.on("tick", () => {
            circles
                .transition()
                .ease(d3.easeLinear)
                .attr("cx", d => d.highlightX)
                .attr("cy", d => d.highlightY);
        });
    }

    
    // Function to highlight groups based on current scroll section
    function updateVisualizationHighlights(currentSection) {
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
            dimNodes(svg, 15, 1000000);
        } else if (currentSection === 2) {
            dimNodes(svg, 1, 1);
            // Only reset simulation if coming from a higher section
            if (previousSection > 2) {
                simulationTickReset(simulation, nodes, circles);
            }
        } else if (currentSection === 3) {
            pareBackNodes(nodes, circles);
            resetNodeOpacityRadius(svg);
            zoomReset(svg, nodes, circles);
        } else if (currentSection === 4) {
            pareBackNodes(nodes, circles);
            zoomIn(svg, nodes, circles);
        } else if (currentSection === 5) {
            zoomIn(svg, nodes, circles, 0.3, 0.7, 1.5);
            pareBackNodesFurther(nodes, circles);
        }
        
        // Update previous section for next time
        previousSection = currentSection;
    }
    
    // Effect to update visualization when section changes
    $effect(() => {
        if (currentSection !== undefined) {
            updateVisualizationHighlights(currentSection);
        }
    });

    onMount(() => {
        
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
                    <p>{@html section.content}</p>
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

    :global(.extreme-offender) {
        background-color: var(--dark-blue);
        color: white;
    }

    :global(.typical-offender) {
        background-color: var(--faint-blue);
        color: white;
    }

    :global(.highlight-text) {
        font-weight: 600;
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
        opacity: 0.9;
        stroke: none;
        stroke-width: 0;
    }
    
    :global(.leaf-circle-hover) {
        fill: #182E6F;
        stroke-width: 0.5px;
        stroke: black;
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