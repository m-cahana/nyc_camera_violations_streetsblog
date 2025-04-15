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
        In 2024, around 2 million drivers sped through school zones
        in New York City, racking up nearly 5 million violations. Below you can see a representative sample of these drivers. Each driver is depicted as a circle, whose size is based on the driver's violations; the larger the circle, the more violations the driver committed. 
    </p>

	<Circles />

    <p>
        Extreme offenders in New York City commit up to 545 violations a year because they can speed through school zones as much as they please. They're hit with a $50 fine per automated violation, but as long as they pay their fines, they won't be taken off the road. This helps explain why there were nearly 19,000 extreme offenders last year. 
    </p>


    <p>
        There used to be a city program in place to change behavior among extreme offenders. Dubbed the Dangerous Vehicle Abatement Program (DVAP), it targeted drivers with 15 or more violations, with the DOT allowed to order them to take a two-hour safety course. In its three years in effect, only 1,600 drivers>took the safety course, out of the tens of thousands who were eligible. Many drivers who took the course continued speeding anyway. The Adams administration and City Council allowed it to <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/dvap-faq.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >expire in 2023</a>.
    </p>

    <p>
        The program rarely took action; <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/evaluation-of-dvap.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >only 12 extreme offenders had their cars seized</a> during the few years the abatement program was active. All other offenders continued driving without truly being restrained. 
    </p>
    

    <p>
        While the city hasn't imposed serious consequences on these offenders, their driving has had deadly consequences for pedestrians. In 2021, a driver with over 90 violations sped the wrong way up Gates Avenue in Fort Greene, <a
        href="https://nyc.streetsblog.org/2021/09/12/slaughter-of-the-innocents-city-in-outrage-over-brooklyn-babys-death-by-reckless-driver"
        target="_blank"
        rel="noopener noreferrer"
        >killing a 3-month old baby.</a> In 2024, another driver with nearly 30 violations <a href="https://nyc.streetsblog.org/2024/01/17/a-pedestrian-was-killed-in-dyker-heights-by-a-driver-with-a-long-record-of-recklessness"
        target="_blank"
        rel="noopener noreferrer">struck and killed
        a pedestrian in Dyker Heights.</a>. Just last month, in March 2025, another extreme offender who would have been subject to DVAP struck a family on Ocean Parkway in Brooklyn, <a href = "https://nyc.streetsblog.org/2025/03/29/slaughter-of-the-innocents-recidivist-speeder-kills-three" target="_blank" rel="noopener noreferrer">killing a mother and two children</a>.
    </p>

    <p>
        As it stands, extreme offenders like these continue speeding through the city, often speeding through the same school zone over and over again. 
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
