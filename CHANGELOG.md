# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2020-04-16

### Added
- Functions:
    - run\_smooth
    - run\_optimization
    - Related functions for display and storage of the results
- Components:
    - AirSourceHeatPump
    - Battery
    - CompressorH2
    - ElectricHeater
    - Electrolyzer
    - EnergyDemandFromCsv
    - EnergySourceFromCsv
    - FuelCellChp
    - GasEngineChpBiogas
    - H2RefuelCoolingSystem
    - Sink
    - StorageH2
    - StratifiedThermalStorage
    - Supply
- Basic tests
- Documentation stub

## [0.3.0] - 2021-04-08

### Changed
- general
    - license changed to dual MIT/Apache-2.0
    - use development branch of oemof.solph
    - included oemof.thermal
    - documentation moved to [Read the Docs](https://smooth.readthedocs.io)
- components
    - renamed Chp to H2Chp
- functions
    - optimization changed to multi-objective evolutionary algortihm based on NSGA-II, optionally with gradient ascent
- models
    - interval time is adjustable
    - components can have 'variable' costs (CAPEX and OPEX), depending on the value of one of its parameters
    - allow None value for fixed cost

### Added
- general
    - tests for all components
    - examples for most components
    - emissions
- components
    - BiogasConverter
    - BiogasSmrPsa
    - ElectrolyzerWasteHeat
    - Gate
    - PemElectrolyzer
    - PowerConverter
    - H2-trailer components (Gates, H2Delivery)
    - VarGrid
    - External components
- functions
    - added debug flag to SimulationParameters
