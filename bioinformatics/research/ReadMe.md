# Research

These are my open-source musings.

## The Starting Gates

The World Health Organization (WHO) maintains a global standard for diagnostic health information, called the *International Classification of Diseases*. WHO has currently published the 11th revision, available here: [ICD-11](https://icd.who.int/en). Keywords, specific disease states, and medical terms can be typed into the [WHO search tool](https://icd.who.int/browse/2024-01/mms/en#149403041), making it easy to start researching areas of human need.

For the most up to date research on available medications, I suggest browsing materials from the [PhRMA](https://www.phrma.org/) website.

**A few observations / notes**:
- Cardiovascular, oncologic, neurologic, and infectious conditions all benefit from genomics-enabled prevention and treatment strategies. Advancing these capabilities can create durable human impact.
- ~95% of attempted solutions to treat a disease will fail. It's an investment of your time, talent, and treasure to go after it. Expect to experience failures. Expect to learn and evolve. 
- If you identify one of the ~5% of solutions that become an effective treatment, you are rewarded with two new problems: access and cost of administration. Coordination of care is tricky. An individual must be prescribed treatment by their physician (sometimes requiring a team of specialists) and gets that prescription filled by their pharmacist. Helping people navigate and afford this journey is itself a challenge.

## Architecture

This folder contains a notebook, `ehrs.ipynb`, that explores health data systems, interoperability, and where genomic results would land in a clinic. A [Flask application](https://flask.palletsprojects.com/en/stable/) is stored in this folder that builds out a useful tool to research genomics.

Styling is split intentionally:
- Shared, reusable primitives/components are provided by the published `prm-studio` package.
- Research-app-specific styles live in `design_system/` and compile to `app/static/css/research-app.css`.

To rebuild app-specific styles:

```console
cd bioinformatics/research/design_system
yarn install
yarn build
```

To run the app, call the flask command from this folder:

```console
poetry run python launch.py
```

More information on the technical code capabilities can be researched in `networks/languages/`. This is not a deployed application; it is built for training and research purposes.

**Data Notices**

- Sample DNA sequences are stored in `data/`. They are simplified teaching examples modeled on well-studied alterations, not real patient data.
- This application is open-source and developed in part with AI agents. Information has not been peer-reviewed.
