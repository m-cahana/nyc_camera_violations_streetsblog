<script>
    import Footer from "$lib/components/footer.svelte";
    import CirclePack from "$lib/components/circle_pack.svelte";
    import { onMount } from 'svelte';

    onMount(() => {
        window.scrollTo(0, 0);
    });
</script>

<main>
	<h1>Drivers Speed Through New York City's School Zones With No Limits</h1>
    <div class="subtitle">April 2025</div>

    <p>
        Last fiscal year, around 3 million drivers sped through school zones
        in New York City, racking up nearly 8 million violations. Below you can see a representative sample of drivers with violations. Each driver is depicted as a circle, whose size is based on the driver's violations; the larger the circle, the more violations the driver committed. 
    </p>

	<CirclePack />

    <p>
        Extreme offenders in New York City can rack up 755 violations because, effectively, they can speed through school zones as much as they please. They're hit with a $50 fine per speeding violation, but as long as they pay their fines, they won't be taken off the road. 
    </p>


    <p>
        There used to be a city program in place to change behavior among extreme offenders. Dubbed the Dangerous Vehicle Abatement Program, in theory it was meant to target drivers with 15+ violations, mandating them to take a two-hour safety course. However, expired in
        <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/dvap-faq.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >2023.</a>. And even when it was active, it only required 1,600 drivers to take the
        safety course, out of the tens of thousands who were eligible. Beyond mandating a
        safety course, the program rarely took further action; only 12 extreme offenders had their cars seized during the few years the abatement program was <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/evaluation-of-dvap.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >active</a>; all other offenders could continue driving without truly being restrained. 
    </p>
    

    <p>
        While the city doesn't impose serious consequences on top offenders, their driving has deadly consequences for pedestrians. In 2021, a driver with over 90 violations sped the wrong way up Gates Avenue in Fort Greene, killing a 3-month old <a
        href="https://nyc.streetsblog.org/2021/09/12/slaughter-of-the-innocents-city-in-outrage-over-brooklyn-babys-death-by-reckless-driver"
        target="_blank"
        rel="noopener noreferrer"
        >baby.</a> In 2024, another driver with nearly 30 violations struck and killed
        a pedestrian in <a href="https://nyc.streetsblog.org/2024/01/17/a-pedestrian-was-killed-in-dyker-heights-by-a-driver-with-a-long-record-of-recklessness"
        target="_blank"
        rel="noopener noreferrer">Dyker Heights.</a>
    </p>

    <p>
        You can see how some top offenders rampantly speed through the city
        in this map. Unless officials enact policy to prevent this behavior,
        there's every reason to expect speeding patterns like these to
        persist in New York, putting the city's children and pedestrians of
        all kind in danger.
    </p>
    
    
    
    
    
    
    
    
    
    
</main>

<Footer />

<style>
	main {
		margin: 0 auto;
		max-width: 800px;
		padding: 1rem;
        font-family: "Helvetica";
		text-align: center;
	}


	h1 {
		font-size: 36px;
        font-style: italic;
        font-weight: 300;
        margin-bottom: 0.2rem;
	}

    p {
        font-size: 16px;
        text-align: left;
        font-weight: 300;
    }

    .subtitle {
        font-size: 20px;
        font-style: italic;
        font-weight: 300;
        margin-top: 0;
    }
</style>
