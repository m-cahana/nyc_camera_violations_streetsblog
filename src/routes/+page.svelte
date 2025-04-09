<script>
    import Footer from "$lib/components/footer.svelte";
    import Circles from "$lib/components/circles.svelte";
    import Map from "$lib/components/map.svelte";
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

	<Circles />

    <p>
        Extreme offenders in New York City commit up to 755 violations because, legally, they can speed through school zones as much as they please. They're hit with a $50 fine per speeding violation, but as long as they pay their fines, they won't be taken off the road. This helps explain why there were nearly 46,000 extreme offenders last year. 
    </p>


    <p>
        There used to be a city program in place to change behavior among extreme offenders. Dubbed the Dangerous Vehicle Abatement Program, it was meant to target drivers with 15+ violations, in theory pushing them to take a two-hour safety course. However,
        <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/dvap-faq.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >it expired in 2023</a>. And even when it was active, it only required 1,600 drivers to take the
        safety course, out of the tens of thousands who were eligible. Beyond mandating a
        safety course, the program rarely took further action; <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/evaluation-of-dvap.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >only 12 extreme offenders had their cars seized</a> during the few years the abatement program was active. All other offenders could continue driving without truly being restrained. 
    </p>
    

    <p>
        While the city doesn't impose serious consequences on these offenders, their driving has deadly consequences for pedestrians. In 2021, a driver with over 90 violations sped the wrong way up Gates Avenue in Fort Greene, <a
        href="https://nyc.streetsblog.org/2021/09/12/slaughter-of-the-innocents-city-in-outrage-over-brooklyn-babys-death-by-reckless-driver"
        target="_blank"
        rel="noopener noreferrer"
        >killing a 3-month old baby.</a> In 2024, another driver with nearly 30 violations <a href="https://nyc.streetsblog.org/2024/01/17/a-pedestrian-was-killed-in-dyker-heights-by-a-driver-with-a-long-record-of-recklessness"
        target="_blank"
        rel="noopener noreferrer">struck and killed
        a pedestrian in Dyker Heights.</a> As it stands, extreme offenders like these continue speeding through the city without strong restraints. They often speed through the same school zone over and over again. 
    </p>

    <Map />
    
    
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
