<script>
    import { onMount } from 'svelte';
    import mapboxgl from 'mapbox-gl';
    import 'mapbox-gl/dist/mapbox-gl.css';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';
    import * as d3 from 'd3';
    import * as turf from '@turf/turf';

    // Props for the component
    let {
        dataPath = '/data/repeat_offenders_lat_long_sample.csv',
        width = 1200,
        height = 600,
        // Add scrolly content for sections
        scrollSections = [
            {
                title: "",
                content: "Consider HSU6447, an <span class = 'extreme-offender'>extreme offender with an average number of violations (19)</span>. This driver's violations were all around Kew Gardens, Queens. Four violations occurred in the same school zone, by the <a href='https://www.kewkids.org/' target='_blank' rel='noopener noreferrer'>Kew Kids Forest School</a>."
            },
            {
                title: "",
                content: "A driver like LDJ6948 is <span class = 'extreme-offender'>even more extreme</span> than average, with 32 violations. Again these violations were concentrated, in this case around schools bordering Jamaica Bay."
            },
            {
                title: "",
                content: "Last year's <span class = 'extreme-offender'>most extreme offender</span> - LCM8254 - sped rampantly, but only in Brooklyn. "
            },
            {
                title: "",
                content: "Most of this driver's violations were concentrated in just a few school zones around Sheepshead Bay, Gravesend, and Brighton Beach. A staggering <span class = 'extreme-offender'>73 violations were commited by one school</span> - <a href='https://www.ahiezeryeshiva.com/' target='_blank' rel='noopener noreferrer'>Ahi Ezer Yeshiva</a> on Ocean Parkway."
            },
        ]
    } = $props();

    // References to DOM elements
    let container;
    let map;
    let mapContainer;
    
    // Component state
    let data = [];
    let processedData = [];
    let currentSection = $state(0);
    let previousSection = 0;
    let currentPlateId = $state('HSU6447');
    let uniquePlateIds = $state([]);
    
    // Data processing function
    function processData(rawData) {
        // Extract unique plate IDs
        uniquePlateIds = [...new Set(rawData.map(d => d.plate_id))].sort();
        
        // Group violations by location (lat/long)
        const violationsByLocation = d3.group(
            rawData,
            d => `${d.lat},${d.long}`
        );
        
        // Convert to array of aggregated violations
        return Array.from(violationsByLocation, ([location, violations]) => {
            const [lat, long] = location.split(',').map(Number);
            const firstViolation = violations[0];
            const count = violations.length;
            const totalFines = count * 50;
            
            // Format location string
            let locationStr = (
                firstViolation.street_name + 
                (firstViolation.intersecting_street || '') + ' ' + 
                firstViolation.violation_county
            );
            
            // Replace @ with & and ensure spaces around &
            locationStr = locationStr.replace(/@/g, ' & ').replace(/\s*&\s*/g, ' & ');
            
            // Convert to title case with special handling for direction abbreviations
            const titleCaseLocation = locationStr
                .split(' ')
                .map(word => {
                    // Handle direction abbreviations
                    if (['EB', 'WB', 'NB', 'SB'].includes(word.toUpperCase())) {
                        return word.toUpperCase();
                    }
                    // Handle other words
                    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
                })
                .join(' ');
            
            return {
                lat,
                long,
                count,
                location: titleCaseLocation,
                totalFines: totalFines.toLocaleString('en-US', { maximumFractionDigits: 0 }),
                // Calculate radius based on count (square root to make area proportional)
                radius: Math.sqrt(violations.length) * 3,
                // Store the original violations for filtering
                violations: violations
            };
        });
    }

    // Function to create the map visualization
    function createVisualization(processedData) {
        console.log("Creating map visualization with", processedData.length, "locations");
        
        // Initialize the Mapbox map
        mapboxgl.accessToken =
            "pk.eyJ1IjoibWljaGFlbC1jYWhhbmEiLCJhIjoiY201ZnhkcG05MDJleTJscHhhNm15MG1kZSJ9.X4X3JWIaV7ju9sBLZgDpHA";

        map = new mapboxgl.Map({
            container: mapContainer,
            style: "mapbox://styles/mapbox/light-v11",
            center: [-73.935242, 40.730610], // [lng, lat] of NYC center
            zoom: 11, // zoom level for NYC view
            attributionControl: false,
            dragPan: false,
            scrollZoom: false,
            doubleClickZoom: false,
            keyboard: false
        });

        // Wait for the map to load before adding data
        map.on('load', async () => {
            // Add a source for the violation points
            map.addSource('violations', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: []
                }
            });

            // Add a layer for the violation circles
            map.addLayer({
                id: 'violation-circles',
                type: 'circle',
                source: 'violations',
                paint: {
                    'circle-radius': ['get', 'radius'],
                    'circle-color': 'rgb(56, 56, 241)',
                    'circle-opacity': 0.7,
                    'circle-stroke-width': 1,
                    'circle-stroke-color': '#ffffff'
                }
            });

            // Add hover effect
            map.on('mousemove', 'violation-circles', (e) => {
                if (e.features.length > 0) {
                    map.getCanvas().style.cursor = 'pointer';
                }
            });

            map.on('mouseleave', 'violation-circles', () => {
                map.getCanvas().style.cursor = '';
            });

            // Add mouseenter event to show tooltip
            map.on('mouseenter', 'violation-circles', (e) => {
                if (e.features.length > 0) {
                    const feature = e.features[0];
                    const coordinates = feature.geometry.coordinates.slice();
                    
                    // Create tooltip
                    const tooltip = document.createElement('div');
                    tooltip.className = 'tooltip';
                    
                    tooltip.innerHTML = `
                        <div class="tooltip-content">
                            <div class="tooltip-row"><strong>Location:</strong> ${feature.properties.location}</div>
                            <div class="tooltip-row"><strong>Violations:</strong> ${feature.properties.count}</div>
                            <div class="tooltip-row"><strong>Total Fines:</strong> $${feature.properties.totalFines}</div>
                        </div>
                    `;
                    
                    // Remove any existing tooltips
                    const existingTooltips = document.querySelectorAll('.tooltip');
                    existingTooltips.forEach(t => t.remove());
                    
                    // Add new tooltip
                    document.body.appendChild(tooltip);
                    
                    // Position tooltip near the cursor
                    const point = map.project(coordinates);
                    tooltip.style.left = `${e.originalEvent.clientX + 15}px`;
                    tooltip.style.top = `${e.originalEvent.clientY - 40}px`;
                    
                    // Show tooltip with a slight delay to prevent flickering
                    setTimeout(() => {
                        tooltip.style.opacity = '1';
                    }, 10);
                }
            });

            // Add mouseleave event to hide tooltip
            map.on('mouseleave', 'violation-circles', () => {
                const tooltips = document.querySelectorAll('.tooltip');
                tooltips.forEach(tooltip => {
                    tooltip.style.opacity = '0';
                    // Remove after fade out
                    setTimeout(() => tooltip.remove(), 200);
                });
            });

            // Show initial view of violations for the target plate
            mapViolationsByPlateId(currentPlateId);
        });
    }

    // Function to map violations for a specific plate ID
    function mapViolationsByPlateId(plateId, centerCoords = null, zoomLevel = 12) {
        if (!map) return;
        
        // Update the current plate ID
        currentPlateId = plateId;
        
        // Filter processed data for the specific plate ID
        const plateViolations = processedData.filter(d => 
            d.violations.some(v => v.plate_id === plateId)
        );
        
        if (plateViolations.length === 0) {
            console.warn(`No violations found for plate ID: ${plateId}`);
            return;
        }

        // Calculate bounds from all points
        const bounds = new mapboxgl.LngLatBounds();
        plateViolations.forEach(d => {
            bounds.extend([d.long, d.lat]);
        });

        // If center coordinates are provided, use them
        if (centerCoords) {
            map.setCenter(centerCoords);
            map.setZoom(zoomLevel);
        } else {
            // Otherwise, fit bounds to all points
            map.fitBounds(bounds, {
                padding: { top: 50, bottom: 50, left: 50, right: 50 }
            });
        }

        // Update the source data
        if (map.getSource('violations')) {
            const geojson = {
                type: 'FeatureCollection',
                features: plateViolations.map(d => ({
                    type: 'Feature',
                    geometry: {
                        type: 'Point',
                        coordinates: [d.long, d.lat]
                    },
                    properties: {
                        location: d.location,
                        count: d.count,
                        totalFines: d.totalFines,
                        radius: d.radius
                    }
                }))};
            // Use the filtered data instead of the original geojson
            map.getSource('violations').setData(geojson);
        }
    }

    // Function to update visualization based on current scroll section
    function updateVisualizationHighlights(currentSection) {
        if (!map) return;
        
        // Apply specific updates based on the current section
        if (currentSection === 0) {
            // Initial view - show all violations for the target plate
            currentPlateId = 'HSU6447';
            mapViolationsByPlateId(currentPlateId);
        } else if (currentSection === 1) {
            // Zoom in to a specific area
            currentPlateId = 'LDJ6948';
            mapViolationsByPlateId(currentPlateId);
        } else if (currentSection === 2) {
            currentPlateId = 'LCM8254';
            mapViolationsByPlateId(currentPlateId);
        } else if (currentSection === 3) {
            currentPlateId = 'LCM8254';
            mapViolationsByPlateId(currentPlateId, [-73.967614, 40.59], 12.8);
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
            .then(rawData => {
                data = rawData; // Store the raw data
                processedData = processData(rawData); // Store the processed data
                return processedData;
            })
            .then(createVisualization)
            .catch((error) => {
                console.error("Error loading CSV:", error);
            });
    });
</script>

<section id="scrolly">
    <!-- Background visualization container -->
    <div class="visualization-container" bind:this={container}>
        <!-- Map container -->
        <div class="map-container" bind:this={mapContainer} style="width: {width}px; height: {height}px;"></div>
        <!-- Title card for plate ID -->
        <div class="title-card">
            <h2>Plate ID: {currentPlateId}</h2>
        </div>
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
    
    .map-container {
        width: v-bind(width + 'px');
        height: v-bind(height + 'px');
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
        z-index: 9999;
        min-width: 200px;
        max-width: 300px;
    }

    :global(.tooltip-content) {
        display: flex;
        flex-direction: column;
    }

    :global(.tooltip-row) {
        margin-bottom: 4px;
    }

    :global(.tooltip-dates) {
        margin-left: 8px;
        font-size: 13px;
    }
    
    /* Ensure Scrolly component has proper z-index */
    :global(.scrolly-container) {
        position: relative;
        z-index: 2;
        pointer-events: none; /* Make container transparent to mouse events */
    }
    
    .title-card {
        position: absolute;
        top: 7%;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 8px 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10;
        pointer-events: auto;
    }
    
    .title-card h2 {
        margin: 0;
        font-size: 16px;
        font-weight: 550;
        font-family: 'Helvetica', sans-serif;
    }
    .title-card select {
        font-size: 16px;
        font-weight: 550;
        font-family: 'Helvetica', sans-serif;
        padding: 2px 6px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: white;
        cursor: pointer;
    }
    
    .title-card select:focus {
        outline: none;
        border-color: rgb(56, 56, 241);
    }
</style>
