# noted

This repository contains a simple event correlation utility for Datadog events.

## Usage

Set the `DD_API_KEY` and `DD_APP_KEY` environment variables then run:

```bash
python3 -m src.correlate
```

The script fetches events from the last hour using the Datadog Events API v2 and groups
related events together. Similarity is calculated using a weighted combination of
title, text and tag overlap. Groups are printed to stdout.

Unit tests can be executed with:

```bash
python3 -m pytest -q
```
