# Django - CAE Workspace > Documents > datetime_recurrence_rules.md

## Description
Recurrence rules are rules for defining repeating datetime events that span multiple days/months/weeks. For example,
events on a calendar or scheduler.

## Outside References
For full documentation on recurrence rules, see:
* https://dateutil.readthedocs.io/en/stable/rrule.html
* https://tools.ietf.org/html/rfc5545

## Recurrence Rule Constants
* `Frequency Constants` - Constant abbreviations used to define frequency:
    * YEARLY
    * MONTHLY
    * WEEKLY
    * DAILY
    * HOURLY
    * MINUTELY
    * SECONDLY
    
* `Weekday Constants` - Constant abbreviations used to define weekdays:
    * MO - Monday
    * TU - Tuesday
    * WE - Wednesday
    * TH - Thursday
    * FR - Friday
    * SA - Saturday
    * SU - Sunday

## Arguments
* `start_time` - A Python datetime value indicating the start of the first event instance.
* `end_time` - A Python datetime value indicating the end of the last event instance.

If the event only occurs once, then no further arguments are necessary. For recurring events, the following values are
required:

* `rrule` - Stands for "recurrence rule". A string denoting the frequency of event repeats. Can be subdivided into:
    * `DTSTART` - The original datetime of the first event instance. Separated from additional args by a '\n' character.
    * `RRULE` - The recurrence rule itself.
        * `FREQ` (required) - How often to repeat the event. Must be one of the `frequency constants`.
        * `INTERVAL` (optional) - Interval between each frequency.
            * For example, an *INTERVAL* of "2" with a *FREQ* of "YEARLY" means "every second year."
        * `COUNT` (optional) - The number of occurances to generate.
            * For example, a *COUNT* of 5 means "create 5 events total, from the first start date."
        * `UNTIL` (optional) - The upper-bound limit of a recurrence. The last event will be the greatest datetime that
        is either less than or equal to this value.
        * `BYWEEKDAY` (optional) - Day of the week to generate events on. Must be one of the `weekday constants`.
            * For example, a *FREQ* of "WEEKLY" with a *BYWEEKDAY* of "TU,TH" means "Every week, on tuesday and thursday".
        * `WKST` (optional) - Day of the week to consider as the "Week start". Must be one of the `weekday constants`.
    * Note that `count` and `until` are mutually exclusive and cannot occur in the same rule at once.
* `duration` - The duration (in microseconds) that each event lasts. Technically can be parsed from `start_time` and `end_time`, but
saving it as a database field helps save computation time with minimal extra storage overhead.
* `exclusions` - Exceptions to generating events with the given rrule. Defined by the datetime that the excluded event
would start on. If multiple exceptions exist for a given event, then they are separated by a '\n' character.

## Time Conversion:
### Basic Conversion
* 1000 Microseconds in 1 Millisecond
* 1000 Milliseconds in 1 Second
* 60 Seconds in 1 Minute
* 60 Minutes in 1 Hour

### Microsecond Conversion
* 1,000,000 Microseconds in 1 Second
* 60,000,000 Microseconds in 1 Minute
* 3,600,000,000 Microseconds in 1 Hour
