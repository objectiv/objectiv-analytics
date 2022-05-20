{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% for item in methods if item not in inherited_members and item != '__init__' %}
    {% if loop.first %}
    {{ _('## Methods') }}

    .. autosummary::
        :toctree:

    {% endif %}
        ~{{ name }}.{{ item }}
    {%- endfor %}

    {% for item in attributes if item not in inherited_members %}
    {% if loop.first %}
    {{ _('## Attributes') }}

    .. autosummary::
        :toctree:

    {% endif %}
        ~{{ name }}.{{ item }}
    {%- endfor %}
