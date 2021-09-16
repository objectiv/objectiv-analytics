from typing import List, Dict, Any, Optional
from abc import ABC
from objectiv_backend.schema.schema_utils import SchemaEntity


class AbstractContext(SchemaEntity, ABC):
    """
        Abstract Contexts define either properties required by Collectors or internal ones for hierarchical
    discrimination purposes.

    All Contexts inherit from AbstractContext. It defines the bare minimum properties every Context must implement.

    For example we never want to mix Location Contexts with Global Contexts and Events may requires specific Contexts
    to be present in their Location Stack. Eg. a NavigationContext instead of a generic SectionContext.

    This ensures that Events are carrying the Contexts they require, making them meaningful and identifiable.

    All Contexts inherit from AbstractContext. It defines the bare minimum properties every Context must implement.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'AbstractContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SchemaEntity.__init__(self, id=id, **kwargs)


class AbstractLocationContext(AbstractContext, ABC):
    """
        This is the abstract parent of all location contexts. LocationContexts are used to populate Trackers or Events
    `location_stack` properties. A Location Stack is meant to describe accurately where an Event originated in the
    UI Eg. Sections, Menus, etc.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'AbstractLocationContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractContext.__init__(self, id=id, **kwargs)


class AbstractGlobalContext(AbstractContext, ABC):
    """
        Global_contexts are used to populate Trackers or Events `global_contexts` properties. They carry information
    that is not related to where the Event originated, such as device, platform or business data.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'AbstractGlobalContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractContext.__init__(self, id=id, **kwargs)


class ApplicationContext(AbstractGlobalContext):
    """
        Global context containing the origin (application id) of the event

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ApplicationContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(self, id=id, **kwargs)


class SectionContext(AbstractLocationContext):
    """
        SectionContexts are special LocationContexts representing a logical area of the UI or the system.
    They can be often reasoned about as being containers of other LocationContexts but not the direct targets of
    Events.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'SectionContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class WebDocumentContext(SectionContext):
    """
        global context about a web document. Should at least contain the current URL.

        Attributes:
        url (str):
                Property containing a (valid) URL
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'WebDocumentContext'

    def __init__(self, url: str, id: str, **kwargs: Optional[Any]):
        """
        :param url: 
            Property containing a (valid) URL
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, url=url, id=id, **kwargs)


class ScreenContext(SectionContext):
    """
        SectionContext for a screen

        Attributes:
        screen (str):
                name of the screen
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ScreenContext'

    def __init__(self, screen: str, id: str, **kwargs: Optional[Any]):
        """
        :param screen: 
            name of the screen
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, screen=screen, id=id, **kwargs)


class ExpandableSectionContext(SectionContext):
    """
        A `SectionContext` that is expandable.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ExpandableSectionContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, id=id, **kwargs)


class MediaPlayerContext(SectionContext):
    """
        A `SectionContext` containing a media player.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'MediaPlayerContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, id=id, **kwargs)


class NavigationContext(SectionContext):
    """
        A `SectionContext` containing navigational elements, for example a menu.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'NavigationContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, id=id, **kwargs)


class OverlayContext(SectionContext):
    """
        A `SectionContext` that is an overlay

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'OverlayContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        SectionContext.__init__(self, id=id, **kwargs)


class ItemContext(AbstractLocationContext):
    """
        ItemContexts are special LocationContexts representing interactive elements of the UI or targets in a system.
    These elements may trigger both Interactive and Non-Interactive Events. Eg. an Input field or a Button.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ItemContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class InputContext(ItemContext):
    """
        A location context, representing user input. For example, a form field, like input.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'InputContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        ItemContext.__init__(self, id=id, **kwargs)


class ActionContext(ItemContext):
    """
        ActionContexts are a more specific version of ItemContext specifically meant to describe actionable Items.
    These represent interactive elements that will trigger an Interactive Event. Eg. A Button or Link.

        Attributes:
        text (str):
                The text of the interactive element or, for visuals, a string describing it
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ActionContext'

    def __init__(self, text: str, id: str, **kwargs: Optional[Any]):
        """
        :param text: 
            The text of the interactive element or, for visuals, a string describing it
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        ItemContext.__init__(self, text=text, id=id, **kwargs)


class ButtonContext(ActionContext):
    """
        interactive element, representing a button.

        Attributes:
        text (str):
                The text of the interactive element or, for visuals, a string describing it
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ButtonContext'

    def __init__(self, text: str, id: str, **kwargs: Optional[Any]):
        """
        :param text: 
            The text of the interactive element or, for visuals, a string describing it
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        ActionContext.__init__(self, text=text, id=id, **kwargs)


class LinkContext(ActionContext):
    """
        interactive element, representing a (hyper) link.

        Attributes:
        href (str):
                URL (href) the link points to
        text (str):
                The text of the interactive element or, for visuals, a string describing it
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'LinkContext'

    def __init__(self,
                 href: str,
                 text: str,
                 id: str,
                 **kwargs: Optional[Any]):
        """
        :param href: 
            URL (href) the link points to
        :param text: 
            The text of the interactive element or, for visuals, a string describing it
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        ActionContext.__init__(self, href=href, text=text, id=id, **kwargs)


class DeviceContext(AbstractGlobalContext):
    """
        Global context containing meta info about the device that emitted the event.

        Attributes:
        user_agent (str):
                String describing the user-agent that emitted the event
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'DeviceContext'

    def __init__(self, user_agent: str, id: str, **kwargs: Optional[Any]):
        """
        :param user_agent: 
            String describing the user-agent that emitted the event
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(
            self, user_agent=user_agent, id=id, **kwargs)


class ErrorContext(AbstractGlobalContext):
    """
        Generic global context to encapsulate any errors

        Attributes:
        message (str):
                Error message
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ErrorContext'

    def __init__(self, message: str, id: str, **kwargs: Optional[Any]):
        """
        :param message: 
            Error message
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(self, message=message, id=id, **kwargs)


class CookieIdContext(AbstractGlobalContext):
    """
        Global context with information needed to reconstruct a user session.

        Attributes:
        cookie_id (str):
                Unique identifier from the session cookie
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'CookieIdContext'

    def __init__(self, cookie_id: str, id: str, **kwargs: Optional[Any]):
        """
        :param cookie_id: 
            Unique identifier from the session cookie
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(
            self, cookie_id=cookie_id, id=id, **kwargs)


class SessionContext(AbstractGlobalContext):
    """
        Context with meta info pertaining to the current session.

        Attributes:
        hit_number (int):
                Hit counter relative to the current session, this event originated in.
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'SessionContext'

    def __init__(self, hit_number: int, id: str, **kwargs: Optional[Any]):
        """
        :param hit_number: 
            Hit counter relative to the current session, this event originated in.
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(
            self, hit_number=hit_number, id=id, **kwargs)


class HttpContext(AbstractGlobalContext):
    """
        Global context with meta information about the agent that sent the event.

        Attributes:
        referer (str):
                Full URL to HTTP referrer of the current page.
        user_agent (str):
                User-agent of the agent that sent the event.
        remote_address (str):
                (public) IP address of the agent that sent the event.
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'HttpContext'

    def __init__(self,
                 referer: str,
                 user_agent: str,
                 remote_address: str,
                 id: str,
                 **kwargs: Optional[Any]):
        """
        :param referer: 
            Full URL to HTTP referrer of the current page.
        :param user_agent: 
            User-agent of the agent that sent the event.
        :param remote_address: 
            (public) IP address of the agent that sent the event.
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(self,
                                       referer=referer,
                                       user_agent=user_agent,
                                       remote_address=remote_address,
                                       id=id,
                                       **kwargs)


class AbstractEvent(SchemaEntity, ABC):
    """
        Events must provide a `name` and optionally can, but most likely will, carry a list of Location and Global
    Contexts. Additionally, every event must have an `ApplicationContext` to be able to distinguish from what
    application the event originated.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'AbstractEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        SchemaEntity.__init__(self,
                              location_stack=location_stack,
                              global_contexts=global_contexts,
                              id=id,
                              time=time,
                              **kwargs)


class NonInteractiveEvent(AbstractEvent):
    """
        Non interactive events, are events that are not (directly) triggered by an interaction. For example:
    Consider the following flow of events:
    1. press play in a video player -> ButtonEvent -> interactive
    2. Videoplayer starting playback -> MediaStartEvent -> non-interactive

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'NonInteractiveEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        AbstractEvent.__init__(self,
                               location_stack=location_stack,
                               global_contexts=global_contexts,
                               id=id,
                               time=time,
                               **kwargs)


class DocumentLoadedEvent(NonInteractiveEvent):
    """
        A non interactive event that is emitted after a document finishes loading. It should provide a
    `WebDocumentContext` which should describe the state (eg. URL) of the event.

    NOTE: with SPA's this probably only happens once, as page (re)loads don't happen after the initial page load

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'DocumentLoadedEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class URLChangeEvent(NonInteractiveEvent):
    """
        non interactive event that is emitted when the URL of a page has changed. Also contains a `WebDocumentContext`
    that details the change.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'URLChangeEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class ApplicationLoadedEvent(NonInteractiveEvent):
    """
        non interactive event that is emitted after an application (eg. SPA) has finished loading.
    Contains a `SectionContext`

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'ApplicationLoadedEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class SectionVisibleEvent(NonInteractiveEvent):
    """
        Non interactive event, emitted after a section (`SectionContext`) has become visible.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'SectionVisibleEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class SectionHiddenEvent(NonInteractiveEvent):
    """
        Non interactive event, emitted after a section (`SectionContext`) has become invisible.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'SectionHiddenEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class VideoEvent(NonInteractiveEvent):
    """
        Family of non interactive events triggered by a video player

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'VideoEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        NonInteractiveEvent.__init__(self,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class VideoLoadEvent(VideoEvent):
    """
        Event emitted after a video completes loading.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'VideoLoadEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        VideoEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class VideoStartEvent(VideoEvent):
    """
        Event emitted after a video starts playback.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'VideoStartEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        VideoEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class VideoStopEvent(VideoEvent):
    """
        Event emitted after a video stops playback.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'VideoStopEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        VideoEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class VideoPauseEvent(VideoEvent):
    """
        Event emitted after a video pauses playback (toggle).

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'VideoPauseEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        VideoEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class InteractiveEvent(AbstractEvent):
    """
        Events that are the direct result of a user interaction. Eg. a Button Click

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'InteractiveEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        AbstractEvent.__init__(self,
                               location_stack=location_stack,
                               global_contexts=global_contexts,
                               id=id,
                               time=time,
                               **kwargs)


class ClickEvent(InteractiveEvent):
    """
        Event triggered by a user clicking on an element

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'ClickEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        InteractiveEvent.__init__(self,
                                  location_stack=location_stack,
                                  global_contexts=global_contexts,
                                  id=id,
                                  time=time,
                                  **kwargs)


class InputChangeEvent(InteractiveEvent):
    """
        Event triggered when user input is modified.

        Attributes:
        location_stack (List[AbstractLocationContext]):
                The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
                deterministically describes where an event took place from global to specific.
                The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        global_contexts (List[AbstractGlobalContext]):
                Global contexts add global / general information about the event. They carry information that is not
                related to where the Event originated (location), such as device, platform or business data.
        id (str):
                Unique identifier for a specific instance of an event. Typically UUID's are a good way of
                implementing this. On the collector side, events should be unique, this means duplicate id's result
                in `not ok` events.
        time (int):
                Timestamp indicating when the event was generated
    """
    _type = 'InputChangeEvent'

    def __init__(self,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param location_stack: 
            The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
            deterministically describes where an event took place from global to specific.
            The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.

        :param global_contexts: 
            Global contexts add global / general information about the event. They carry information that is not
            related to where the Event originated (location), such as device, platform or business data.
        :param id: 
            Unique identifier for a specific instance of an event. Typically UUID's are a good way of
            implementing this. On the collector side, events should be unique, this means duplicate id's result
            in `not ok` events.
        :param time: 
            Timestamp indicating when the event was generated
        """
        InteractiveEvent.__init__(self,
                                  location_stack=location_stack,
                                  global_contexts=global_contexts,
                                  id=id,
                                  time=time,
                                  **kwargs)


def make_context(_type: str, **kwargs) -> AbstractContext:
    if _type == "AbstractContext":
        return AbstractContext(**kwargs)
    if _type == "AbstractLocationContext":
        return AbstractLocationContext(**kwargs)
    if _type == "AbstractGlobalContext":
        return AbstractGlobalContext(**kwargs)
    if _type == "ApplicationContext":
        return ApplicationContext(**kwargs)
    if _type == "SectionContext":
        return SectionContext(**kwargs)
    if _type == "WebDocumentContext":
        return WebDocumentContext(**kwargs)
    if _type == "ScreenContext":
        return ScreenContext(**kwargs)
    if _type == "ExpandableSectionContext":
        return ExpandableSectionContext(**kwargs)
    if _type == "MediaPlayerContext":
        return MediaPlayerContext(**kwargs)
    if _type == "NavigationContext":
        return NavigationContext(**kwargs)
    if _type == "OverlayContext":
        return OverlayContext(**kwargs)
    if _type == "ItemContext":
        return ItemContext(**kwargs)
    if _type == "InputContext":
        return InputContext(**kwargs)
    if _type == "ActionContext":
        return ActionContext(**kwargs)
    if _type == "ButtonContext":
        return ButtonContext(**kwargs)
    if _type == "LinkContext":
        return LinkContext(**kwargs)
    if _type == "DeviceContext":
        return DeviceContext(**kwargs)
    if _type == "ErrorContext":
        return ErrorContext(**kwargs)
    if _type == "CookieIdContext":
        return CookieIdContext(**kwargs)
    if _type == "SessionContext":
        return SessionContext(**kwargs)
    if _type == "HttpContext":
        return HttpContext(**kwargs)
    return AbstractContext(**kwargs)


def make_event(_type: str, **kwargs) -> AbstractEvent:
    if _type == "AbstractEvent":
        return AbstractEvent(**kwargs)
    if _type == "NonInteractiveEvent":
        return NonInteractiveEvent(**kwargs)
    if _type == "DocumentLoadedEvent":
        return DocumentLoadedEvent(**kwargs)
    if _type == "URLChangeEvent":
        return URLChangeEvent(**kwargs)
    if _type == "ApplicationLoadedEvent":
        return ApplicationLoadedEvent(**kwargs)
    if _type == "SectionVisibleEvent":
        return SectionVisibleEvent(**kwargs)
    if _type == "SectionHiddenEvent":
        return SectionHiddenEvent(**kwargs)
    if _type == "VideoEvent":
        return VideoEvent(**kwargs)
    if _type == "VideoLoadEvent":
        return VideoLoadEvent(**kwargs)
    if _type == "VideoStartEvent":
        return VideoStartEvent(**kwargs)
    if _type == "VideoStopEvent":
        return VideoStopEvent(**kwargs)
    if _type == "VideoPauseEvent":
        return VideoPauseEvent(**kwargs)
    if _type == "InteractiveEvent":
        return InteractiveEvent(**kwargs)
    if _type == "ClickEvent":
        return ClickEvent(**kwargs)
    if _type == "InputChangeEvent":
        return InputChangeEvent(**kwargs)
    return AbstractEvent(**kwargs)


def make_event_from_dict(obj: Dict[str, Any]) -> AbstractEvent:
    if not ('_type' in obj and 'location_stack' in obj and 'global_contexts' in obj):
        raise Exception('missing arguments')
    obj['location_stack'] = [make_context(**c) for c in obj['location_stack']]
    obj['global_contexts'] = [make_context(
        **c) for c in obj['global_contexts']]

    return make_event(**obj)
