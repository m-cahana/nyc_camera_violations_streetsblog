<script>
	import Scrolly from "$lib/components/helpers/scrolly.svelte";
	let value = $state(0);
</script>

<section id="scrolly">
	<h2>Scrolly <span>{value || "-"}</span></h2>
	<div class="spacer"></div>
	<Scrolly bind:value>
		{#each [0, 1, 2] as text, i}
			{@const active = value === i}
			<div class="step" class:active>
				<p>{text}</p>
			</div>
		{/each}
	</Scrolly>
	<div class="spacer"></div>
</section>

<style>
	h2 {
		position: sticky;
		top: 4em;
		font-weight: 300;
		font-family: "Helvetica";
	}

	.spacer {
		height: 75vh;
		
	}

	.step {
		height: 80vh;
		background: var(--color-gray-100);
		text-align: center;
	}

	.step p {
		padding: 1rem;
		font-weight: 300;
		font-family: "Helvetica";
	}

</style>