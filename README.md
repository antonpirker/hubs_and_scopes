# New Hubs and Scopes API

## The way to the new API (work in progress):

- Deprecate global API functions as defined in RFC
- Rename `Hub` -> `LegacyHub`, `Scope` -> `LegacyScope`, `Client -> LegacyClient` and create aliases so the old names still work
- Move all the functions from Hub to Scope and make the existing Hub functions call the ones on the scope.
- Create `NewScope` and `NewClient` and add new global API functions.
- Make integrations work with `NewScope` and `NewClient` and new global API functions.

Until here nothing should be breaking

- Remove the aliases and rename `NewScope` to `Scope` and `NewClient` to `Client`. Remove `Hub`. THIS IS BREAKING AND NEEDS A MAJOR