<script>
    import CirclePack from "$lib/components/circle_pack.svelte";
    
    // Example text content for scrolly steps
    const scrollyTexts = [
        `<h2>School Zone Speed Camera Violations</h2>
        <p>In New York City, thousands of vehicles are caught speeding in school zones every day.</p>`,
        
        `<h2>Repeat Offenders</h2>
        <p>The data shows that many vehicles are repeat offenders, with some accumulating dozens of violations.</p>`,
        
        `<h2>Visualization Overview</h2>
        <p>This visualization groups vehicles by their number of violations:</p>
        <ul>
            <li>Small circles (1-2 violations): Occasional speeders</li>
            <li>Medium circles (3-15 violations): Regular offenders</li>
            <li>Large circles (16+ violations): Chronic speeders</li>
        </ul>`,
        
        `<h2>Impact</h2>
        <p>These violations represent dangerous driving behavior around schools where children are present. Each circle represents a vehicle that has been caught speeding in a school zone.</p>`
    ];
</script>

<div class="container">
    <h1>School Zone Speed Camera Violations</h1>
    <p class="intro">Scroll down to explore data about vehicles caught speeding in school zones.</p>
    
    <CirclePack 
        dataPath="/data/school_zone_violations_sparser.csv"
        scrollyTexts={scrollyTexts}
    />
</div>

<style>
    .container {
        max-width: 100%;
        margin: 0 auto;
        padding: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .intro {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    :global(h2) {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    :global(p) {
        font-size: 1.1rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    :global(ul) {
        padding-left: 1.5rem;
    }
    
    :global(li) {
        margin-bottom: 0.5rem;
    }
</style> 