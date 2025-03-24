<script>
	import Scrolly from "$lib/components/scrolly.svelte";
    import Footer from "$lib/components/footer.svelte";
</script>

<main>
	<h1>Drivers Speed Through New York City's School Zones With No Limits</h1>
    <div class="subtitle">March 2025</div>

    <p>
        Last fiscal year, around 3 million drivers sped through school zones
        in New York City, racking up nearly 8 million violations.
    </p>

    <p>
        Each dot here represents a driver. As you move right, you'll see how
        violations pile up across drivers. While most drivers were caught
        speeding just once or twice, a small group of repeat offenders sped
        rampantly, accounting for a disproportionate share of all the city's
        violations.
    </p>

	<Scrolly />

    <p>
        Even when limiting one's view to the top 50% of drivers, things
        start to look disproportionate. These drivers all sped through
        school zones at least twice last year, and together accounted for
        over 80% of all violations.
    </p>


    <p>
        Things get even more extreme when you look at the very top of the
        distribution. The top 1% of drivers - about 30,000 license plates -
        accounted for over a tenth of school zone violations last year. All
        told, they sped through school zones nearly 850,000 times.
    </p>

    <p>
        Each of these top offenders sped at least 17 times. The worst
        offender sped over 750 times - more than twice a day on average.
    </p>

    <p>
        This small group of top offenders drove mostly around Brooklyn and
        Queens, New York's two most populous boroughs. These boroughs also
        have light traffic, relative to Manhattan at least, which may allow
        for easier speeding.
    </p>
    
    <p>
        As evidenced by one driver racking up over 750 violations, top
        offenders in New York can speed through school zones as much as they
        please. They pay a $50 fine per violation, but their cars aren't
        taken off the road, no matter how often they're fined. A city
        abatement program used to require some drivers with 15 or more
        violations to take a two-hour safety course, but it expired in
        <a
        href="https://www.nyc.gov/html/dot/downloads/pdf/dvap-faq.pdf"
        target="_blank"
        rel="noopener noreferrer"
        >2023.</a>
    </p>

    <p>
        Even when it was active, it only required 1,600 drivers to take the
        course, out of the tens of thousands eligible. Beyond mandating a
        safety course, the city rarely took other action, only seizing cars
        from 12 top offenders during the few years the abatement program was
        <a
          href="https://www.nyc.gov/html/dot/downloads/pdf/evaluation-of-dvap.pdf"
          target="_blank"
          rel="noopener noreferrer"
          >active.</a
        >
    </p>

    <p>
        While the city doesn't impose serious consequences on top offenders,
            their driving has deadly consequences for pedestrians. In 2021, a
            driver with over 90 violations sped the wrong way up Gates Avenue in
            Fort Greene, killing a 3-month old
            <a
              href="https://nyc.streetsblog.org/2021/09/12/slaughter-of-the-innocents-city-in-outrage-over-brooklyn-babys-death-by-reckless-driver"
              target="_blank"
              rel="noopener noreferrer"
              >baby.</a
            >
            In 2024, another driver with nearly 30 violations struck and killed
            a pedestrian in
            <a
              href="https://nyc.streetsblog.org/2024/01/17/a-pedestrian-was-killed-in-dyker-heights-by-a-driver-with-a-long-record-of-recklessness"
              target="_blank"
              rel="noopener noreferrer"
              >Dyker Heights.</a
            >
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
