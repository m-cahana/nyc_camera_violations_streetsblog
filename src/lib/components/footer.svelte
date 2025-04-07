<footer>
    <div class="line"></div>
    <div class="footer-content">
        <p class = 'attribution'>Created by Michael Cahana. All code for this project can be viewed on <a href = 'https://github.com/m-cahana/pentagon_dei_purge' target="_blank" rel="noopener noreferrer" >GitHub</a>.</p>

        <h2>Methodology</h2>
        <p class = 'methodology'>
            School zone violation data for the 2024 fiscal year was sourced from
            <a
              href="https://data.cityofnewyork.us/City-Government/Parking-Violations-Issued-Fiscal-Year-2024/pvqr-7yc4/about_data"
              target="_blank"
              rel="noopener noreferrer"
              >NYC's open data portal</a
            >. Fine amounts were pulled from the portal as well. <br /><br />
            At over 8 million instances, school zone violations are costly to
            store in memory. Violation data was aggregated up to the license
            plate level, and then information about specific violation instances
            (like a violation's street and cross-street) was pulled as needed
            via the
            <a
              href="https://dev.socrata.com/foundry/data.cityofnewyork.us/pvqr-7yc4"
              target="_blank"
              >Socrata Open Data API</a
            >. Those streets/cross-streets were then converted into latitude and
            longitude coordinates using the
            <a
              href="https://developers.google.com/maps/documentation/geocoding/overview"
              target="_blank"
              >Google Maps Geocoding API.</a
            >
        </p>

        <p class = 'methodology'>
            Since violations are so numerous, they couldn't all be presented
            interactively in this project. A sample of violations from across
            the distribution of offenders is presented instead. But note that
            all statistics displayed in this project are drawn from
            the entire distribution of data, not just the small representative
            sample.
        </p>

        <p class = 'methodology'>
            Note that a "typical offender" was selected as the the median offender in the sample, who has 1 violation. It's also true that 52% of offenders have only 1 violation, so the 1-violation offender represents not just the median but also the mode - literally the most common offender.
        </p>
    </div>
</footer>

<style>
    footer {
        padding: 2rem 5%;
        margin-top: 2rem;
    }

    p {
        font-size: 14px;
        text-align: left;
    }

    .attribution {
        font-style: italic;
    }

    .methodology {
        padding-left: 1rem;
    }

    h2 {
        font-size: 18px;
        font-family: "Helvetica";
        font-weight: 300;
        font-style: italic;
        margin-bottom: 1rem;
        text-align: left;
    }

    .line {
        border-top: 1px solid black;
        width: 100%;
        margin-bottom: 1rem;
    }

    .footer-content {
        font-family: "Helvetica";
        font-weight: 300;
        text-align: center;
    }

</style> 