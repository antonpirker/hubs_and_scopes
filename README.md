# New Hubs and Scopes API

## The way to the new API (work in progress):

- Deprecate global API functions as defined in RFC
- Create new `Scope2` and `Client2` and `api2.py` and put new stuff there
- Move all the functions from Hub to Scope and make the existing Hub functions call the ones on the scope.
- Make all 40+ integrations work with `Scope2` and `Client2` and new `api2.py`.

- Make `Scope` call functions in `Scope2`, `Client` in `Client2` and `api.py` in `api2.py`, make `Hub` a hollow shell that calls stuff in `Scope12`
- Make deprecation warnings in all `Scope`, `Client` and `api.py` and `Hub` functions that will be removed

Until here nothing should be breaking

- Remove deprecated functions in `Scope`, `Client` and `api.py` and `Hub` and rename `Scope2` > `Scope`, `Client2` > `Client`, `api2.py` > `api.py`. Remove `Hub`