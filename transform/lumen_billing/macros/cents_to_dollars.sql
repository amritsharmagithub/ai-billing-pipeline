-- Converts a whole-number cents column to exact dollars, for example 51500 -> 515.00.
-- Uses DECIMAL math only. Plain division (cents / 100) would give an inexact DOUBLE.

{% macro cents_to_dollars(column_name) %}
    cast(cast({{ column_name }} as decimal(18, 0)) * 0.01 as decimal(18, 2))
{% endmacro %}
