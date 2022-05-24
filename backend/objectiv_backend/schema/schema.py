from typing import List, Dict, Any, Optional
from abc import ABC
from objectiv_backend.schema.schema_utils import SchemaEntity


class AbstractContext(SchemaEntity, ABC):
    """
        AbstractContext defines the bare minimum properties for every Context. All Contexts inherit from it.

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


class AbstractGlobalContext(AbstractContext, ABC):
    """
        This is the abstract parent of all Global Contexts. Global contexts add general information to an Event.

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
        A GlobalContext describing in which app the event happens, like a website or iOS app.

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


class HttpContext(AbstractGlobalContext):
    """
        A GlobalContext describing meta information about the agent that sent the event.

        Attributes:
        referrer (str):
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
                 referrer: str,
                 user_agent: str,
                 id: str,
                 remote_address: str = None,
                 **kwargs: Optional[Any]):
        """
        :param referrer: 
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
                                       referrer=referrer,
                                       user_agent=user_agent,
                                       remote_address=remote_address,
                                       id=id,
                                       **kwargs)


class PathContext(AbstractGlobalContext):
    """
        A GlobalContext describing the path where the user is when an event is sent.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'PathContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(self, id=id, **kwargs)


class SessionContext(AbstractGlobalContext):
    """
        A GlobalContext describing meta information about the current session.

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


class MarketingContext(AbstractGlobalContext):
    """
        a context that captures marketing channel info, so users can do attribution, campaign
    effectiveness and other models

        Attributes:
        source (str):
                Identifies the advertiser, site, publication, etc
        medium (str):
                Advertising or marketing medium: cpc, banner, email newsletter, etc
        campaign (str):
                Individual campaign name, slogan, promo code, etc
        term (str):
                [Optional] Search keywords
        content (str):
                [Optional] Used to differentiate similar content, or links within the same ad
        source_platform (str):
                [Optional] To differentiate similar content, or links within the same ad.
        creative_format (str):
                [Optional] Identifies the creative used (e.g., skyscraper, banner, etc).
        marketing_tactic (str):
                [Optional] Identifies the marketing tactic used (e.g., onboarding, retention, acquisition etc).
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'MarketingContext'

    def __init__(self,
                 source: str,
                 medium: str,
                 campaign: str,
                 id: str,
                 term: str = None,
                 content: str = None,
                 source_platform: str = None,
                 creative_format: str = None,
                 marketing_tactic: str = None,
                 **kwargs: Optional[Any]):
        """
        :param source: 
            Identifies the advertiser, site, publication, etc
        :param medium: 
            Advertising or marketing medium: cpc, banner, email newsletter, etc
        :param campaign: 
            Individual campaign name, slogan, promo code, etc
        :param term: 
            [Optional] Search keywords
        :param content: 
            [Optional] Used to differentiate similar content, or links within the same ad
        :param source_platform: 
            [Optional] To differentiate similar content, or links within the same ad.
        :param creative_format: 
            [Optional] Identifies the creative used (e.g., skyscraper, banner, etc).
        :param marketing_tactic: 
            [Optional] Identifies the marketing tactic used (e.g., onboarding, retention, acquisition etc).
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractGlobalContext.__init__(self,
                                       source=source,
                                       medium=medium,
                                       campaign=campaign,
                                       term=term,
                                       content=content,
                                       source_platform=source_platform,
                                       creative_format=creative_format,
                                       marketing_tactic=marketing_tactic,
                                       id=id,
                                       **kwargs)


class AbstractLocationContext(AbstractContext, ABC):
    """
        AbstractLocationContext are the abstract parents of all Location Contexts. Location Contexts are meant to describe where an event originated from in the visual UI.

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


class InputContext(AbstractLocationContext):
    """
        A Location Context that describes an element that accepts user input, i.e. a form field.

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
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class PressableContext(AbstractLocationContext):
    """
        An Location Context that describes an interactive element (like a link, button, icon),
    that the user can press and will trigger an Interactive Event.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'PressableContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class LinkContext(PressableContext):
    """
        A PressableContext that contains an href.

        Attributes:
        href (str):
                URL (href) the link points to.

        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'LinkContext'

    def __init__(self, href: str, id: str, **kwargs: Optional[Any]):
        """
        :param href: 
            URL (href) the link points to.

        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        PressableContext.__init__(self, href=href, id=id, **kwargs)


class RootLocationContext(AbstractLocationContext):
    """
        A Location Context that uniquely represents the top-level UI location of the user.



        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'RootLocationContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class ExpandableContext(AbstractLocationContext):
    """
        A Location Context that describes a section of the UI that can expand & collapse.



        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ExpandableContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class MediaPlayerContext(AbstractLocationContext):
    """
        A Location Context that describes a section of the UI containing a media player.



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
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class NavigationContext(AbstractLocationContext):
    """
        A Location Context that describes a section of the UI containing navigational elements, for example a menu.



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
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class OverlayContext(AbstractLocationContext):
    """
        A Location Context that describes a section of the UI that represents an overlay, i.e. a Modal.

    .

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
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class ContentContext(AbstractLocationContext):
    """
        A Location Context that describes a logical section of the UI that contains other Location Contexts. Enabling Data Science to analyze this section specifically.

        Attributes:
        id (str):
                A unique string identifier to be combined with the Context Type (`_type`)
                for Context instance uniqueness.
    """
    _type = 'ContentContext'

    def __init__(self, id: str, **kwargs: Optional[Any]):
        """
        :param id: 
            A unique string identifier to be combined with the Context Type (`_type`)
            for Context instance uniqueness.
        """
        AbstractLocationContext.__init__(self, id=id, **kwargs)


class AbstractEvent(SchemaEntity, ABC):
    """
        This is the abstract parent of all Events.

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


class InteractiveEvent(AbstractEvent):
    """
        The parent of Events that are the direct result of a user interaction, e.g. a button click.

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


class NonInteractiveEvent(AbstractEvent):
    """
        The parent of Events that are not directly triggered by a user action.

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


class ApplicationLoadedEvent(NonInteractiveEvent):
    """
        A NonInteractive event that is emitted after an application (eg. SPA) has finished loading.

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


class FailureEvent(NonInteractiveEvent):
    """
        A NonInteractiveEvent that is sent when a user action results in a error,
    like an invalid email when sending a form.

        Attributes:
        message (str):
                Failure message.
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
    _type = 'FailureEvent'

    def __init__(self,
                 message: str,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param message: 
            Failure message.
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
                                     message=message,
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


class PressEvent(InteractiveEvent):
    """
        An InteractiveEvent that is sent when a user presses on a pressable element
    (like a link, button, icon).

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
    _type = 'PressEvent'

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


class HiddenEvent(NonInteractiveEvent):
    """
        A NonInteractiveEvent that's emitted after a LocationContext has become invisible.

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
    _type = 'HiddenEvent'

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


class VisibleEvent(NonInteractiveEvent):
    """
        A NonInteractiveEvent that's emitted after a section LocationContext has become visible.



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
    _type = 'VisibleEvent'

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


class SuccessEvent(NonInteractiveEvent):
    """
        A NonInteractiveEvent that is sent when a user action is successfully completed,
    like sending an email form.

        Attributes:
        message (str):
                Success message.
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
    _type = 'SuccessEvent'

    def __init__(self,
                 message: str,
                 location_stack: List[AbstractLocationContext],
                 global_contexts: List[AbstractGlobalContext],
                 id: str,
                 time: int,
                 **kwargs: Optional[Any]):
        """
        :param message: 
            Success message.
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
                                     message=message,
                                     location_stack=location_stack,
                                     global_contexts=global_contexts,
                                     id=id,
                                     time=time,
                                     **kwargs)


class MediaEvent(NonInteractiveEvent):
    """
        The parent of non-interactive events that are triggered by a media player.
    It requires a MediaPlayerContext to detail the origin of the event.

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
    _type = 'MediaEvent'

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


class MediaLoadEvent(MediaEvent):
    """
        A MediaEvent that's emitted after a media item completes loading.



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
    _type = 'MediaLoadEvent'

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
        MediaEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class MediaPauseEvent(MediaEvent):
    """
        A MediaEvent that's emitted after a media item pauses playback.



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
    _type = 'MediaPauseEvent'

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
        MediaEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class MediaStartEvent(MediaEvent):
    """
        A MediaEvent that's emitted after a media item starts playback.



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
    _type = 'MediaStartEvent'

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
        MediaEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


class MediaStopEvent(MediaEvent):
    """
        A MediaEvent that's emitted after a media item stops playback.



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
    _type = 'MediaStopEvent'

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
        MediaEvent.__init__(self,
                            location_stack=location_stack,
                            global_contexts=global_contexts,
                            id=id,
                            time=time,
                            **kwargs)


def make_context(_type: str, **kwargs) -> AbstractContext:
    if _type == "AbstractContext":
        return AbstractContext(**kwargs)
    if _type == "AbstractGlobalContext":
        return AbstractGlobalContext(**kwargs)
    if _type == "ApplicationContext":
        return ApplicationContext(**kwargs)
    if _type == "CookieIdContext":
        return CookieIdContext(**kwargs)
    if _type == "HttpContext":
        return HttpContext(**kwargs)
    if _type == "PathContext":
        return PathContext(**kwargs)
    if _type == "SessionContext":
        return SessionContext(**kwargs)
    if _type == "MarketingContext":
        return MarketingContext(**kwargs)
    if _type == "AbstractLocationContext":
        return AbstractLocationContext(**kwargs)
    if _type == "InputContext":
        return InputContext(**kwargs)
    if _type == "PressableContext":
        return PressableContext(**kwargs)
    if _type == "LinkContext":
        return LinkContext(**kwargs)
    if _type == "RootLocationContext":
        return RootLocationContext(**kwargs)
    if _type == "ExpandableContext":
        return ExpandableContext(**kwargs)
    if _type == "MediaPlayerContext":
        return MediaPlayerContext(**kwargs)
    if _type == "NavigationContext":
        return NavigationContext(**kwargs)
    if _type == "OverlayContext":
        return OverlayContext(**kwargs)
    if _type == "ContentContext":
        return ContentContext(**kwargs)
    return AbstractContext(**kwargs)


def make_event(_type: str, **kwargs) -> AbstractEvent:
    if _type == "AbstractEvent":
        return AbstractEvent(**kwargs)
    if _type == "InteractiveEvent":
        return InteractiveEvent(**kwargs)
    if _type == "NonInteractiveEvent":
        return NonInteractiveEvent(**kwargs)
    if _type == "ApplicationLoadedEvent":
        return ApplicationLoadedEvent(**kwargs)
    if _type == "FailureEvent":
        return FailureEvent(**kwargs)
    if _type == "InputChangeEvent":
        return InputChangeEvent(**kwargs)
    if _type == "PressEvent":
        return PressEvent(**kwargs)
    if _type == "HiddenEvent":
        return HiddenEvent(**kwargs)
    if _type == "VisibleEvent":
        return VisibleEvent(**kwargs)
    if _type == "SuccessEvent":
        return SuccessEvent(**kwargs)
    if _type == "MediaEvent":
        return MediaEvent(**kwargs)
    if _type == "MediaLoadEvent":
        return MediaLoadEvent(**kwargs)
    if _type == "MediaPauseEvent":
        return MediaPauseEvent(**kwargs)
    if _type == "MediaStartEvent":
        return MediaStartEvent(**kwargs)
    if _type == "MediaStopEvent":
        return MediaStopEvent(**kwargs)
    return AbstractEvent(**kwargs)


def make_event_from_dict(obj: Dict[str, Any]) -> AbstractEvent:
    if not ('_type' in obj and 'location_stack' in obj and 'global_contexts' in obj):
        raise Exception('missing arguments')
    obj['location_stack'] = [make_context(**c) for c in obj['location_stack']]
    obj['global_contexts'] = [make_context(
        **c) for c in obj['global_contexts']]

    return make_event(**obj)
