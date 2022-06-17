/*
 * Copyright 2022 Objectiv B.V.
 */

import { expectToThrow } from '@objectiv/testing-tools';
import { RecordedEvent } from '@objectiv/tracker-core';
import { RecordedEvents } from '../src/RecordedEvents';

describe('RecordedEvents', () => {
  const events = [
    {
      _type: 'ApplicationLoadedEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'ApplicationLoadedEvent#1',
    },
    {
      _type: 'MediaLoadEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'video',
        },
        {
          _type: 'ContentContext',
          id: 'modeling',
        },
        {
          _type: 'MediaPlayerContext',
          id: '2-minute-video',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/video',
        },
      ],
      id: 'MediaLoadEvent#1',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'logo',
          href: '/',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#1',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'contact-us',
          href: 'mailto:hi@objectiv.io',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#10',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'video',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'about-us',
          href: '/about',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/video',
        },
      ],
      id: 'PressEvent#2',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'blog',
          href: '/blog',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#3',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'jobs',
          href: '/jobs',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#4',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'faq',
          href: 'http://localhost:3000/docs/home/the-project/faq',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#5',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'docs',
          href: 'http://localhost:3000/docs',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#6',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'video',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'github',
          href: 'https://github.com/objectiv/objectiv-analytics',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/video',
        },
      ],
      id: 'PressEvent#7',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'slack',
          href: '/join-slack',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#8',
    },
    {
      _type: 'PressEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'NavigationContext',
          id: 'navbar-top',
        },
        {
          _type: 'LinkContext',
          id: 'twitter',
          href: 'https://twitter.com/objectiv_io',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'PressEvent#9',
    },
    {
      _type: 'VisibleEvent',
      location_stack: [
        {
          _type: 'RootLocationContext',
          id: 'home',
        },
        {
          _type: 'PressableContext',
          id: 'star-us-notification',
        },
        {
          _type: 'OverlayContext',
          id: 'star-us-notification-overlay',
        },
      ],
      global_contexts: [
        {
          _type: 'HttpContext',
          id: 'http_context',
          referrer: '',
          user_agent: 'mocked-user-agent',
          remote_address: null,
        },
        {
          _type: 'ApplicationContext',
          id: 'objectiv-website-dev',
        },
        {
          _type: 'PathContext',
          id: 'http://localhost:3000/',
        },
      ],
      id: 'VisibleEvent#1',
    },
  ];

  const recordedEvents = new RecordedEvents(events);

  describe('filter', () => {
    it('should throw', async () => {
      // @ts-ignore
      expectToThrow(() => recordedEvents.filter(), `Invalid event filter options: undefined`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.filter(null), `Invalid event filter options: null`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.filter({}), `Invalid event filter options: {}`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.filter(123), `Invalid event filter options: 123`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.filter([]), `Invalid event filter options: `);
    });

    it('should filter by event _type', async () => {
      expect(recordedEvents.filter('ApplicationLoadedEvent').events).toStrictEqual([events[0]]);
      expect(recordedEvents.filter('MediaLoadEvent').events).toStrictEqual([events[1]]);
      expect(recordedEvents.filter('PressEvent').events).toStrictEqual(events.slice(0, -1).slice(2));
      expect(recordedEvents.filter('VisibleEvent').events).toStrictEqual([events[events.length - 1]]);
    });

    it('should filter by event _types', async () => {
      expect(recordedEvents.filter(['MediaLoadEvent', 'VisibleEvent']).events).toStrictEqual([
        events[1],
        events[events.length - 1],
      ]);
    });

    it('should filter by a predicate', async () => {
      expect(
        recordedEvents.filter(
          (recordedEvent: RecordedEvent) =>
            ['MediaLoadEvent', 'VisibleEvent'].includes(recordedEvent._type) &&
            recordedEvent.location_stack.some(
              ({ _type, id }) => _type === 'OverlayContext' && id === 'star-us-notification-overlay'
            )
        ).events
      ).toStrictEqual([events[events.length - 1]]);
    });

    it('should allow to chain filter', async () => {
      expect(recordedEvents.filter(['MediaLoadEvent', 'VisibleEvent']).filter('VisibleEvent').events).toStrictEqual([
        events[events.length - 1],
      ]);
    });
  });

  describe('withLocationContext', () => {
    it('should throw', async () => {
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext(),
        `Invalid location context filter name option: undefined`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext(null),
        `Invalid location context filter name option: null`
      );
      // @ts-ignore
      expectToThrow(() => recordedEvents.withLocationContext({}), `Invalid location context filter name option: {}`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withLocationContext(123), `Invalid location context filter name option: 123`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withLocationContext([]), `Invalid location context filter name option: `);
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext('ContentContext', null),
        `Invalid location context filter id option: null`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext('ContentContext', {}),
        `Invalid location context filter id option: {}`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext('ContentContext', 123),
        `Invalid location context filter id option: 123`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withLocationContext('ContentContext', []),
        `Invalid location context filter id option: `
      );
    });

    it('should filter by location context', async () => {
      expect(recordedEvents.withLocationContext('MediaPlayerContext').events).toStrictEqual([events[1]]);
      expect(recordedEvents.withLocationContext('PressableContext').events).toStrictEqual([events[events.length - 1]]);
      expect(recordedEvents.withLocationContext('LinkContext').events).toStrictEqual(events.slice(0, -1).slice(2));
    });

    it('should filter by location context and id', async () => {
      expect(recordedEvents.withLocationContext('LinkContext', 'logo').events).toStrictEqual([events[2]]);
    });

    it('should allow to chain withLocationContext', async () => {
      expect(
        recordedEvents.withLocationContext('LinkContext').withLocationContext('LinkContext', 'twitter').events
      ).toStrictEqual([events[11]]);
    });
  });

  describe('withGlobalContext', () => {
    it('should throw', async () => {
      // @ts-ignore
      expectToThrow(() => recordedEvents.withGlobalContext(), `Invalid global context filter name option: undefined`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withGlobalContext(null), `Invalid global context filter name option: null`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withGlobalContext({}), `Invalid global context filter name option: {}`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withGlobalContext(123), `Invalid global context filter name option: 123`);
      // @ts-ignore
      expectToThrow(() => recordedEvents.withGlobalContext([]), `Invalid global context filter name option: `);
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withGlobalContext('ApplicationContext', null),
        `Invalid location context filter id option: null`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withGlobalContext('ApplicationContext', {}),
        `Invalid location context filter id option: {}`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withGlobalContext('ApplicationContext', 123),
        `Invalid location context filter id option: 123`
      );
      expectToThrow(
        // @ts-ignore
        () => recordedEvents.withGlobalContext('ApplicationContext', []),
        `Invalid location context filter id option: `
      );
    });

    it('should filter by global context', async () => {
      expect(recordedEvents.withGlobalContext('PathContext').events).toStrictEqual(events);
    });

    it('should filter by global context and id', async () => {
      expect(recordedEvents.withGlobalContext('PathContext', 'http://localhost:3000/video').events).toStrictEqual([
        events[1],
        events[4],
        events[9],
      ]);
    });

    it('should allow to chain withGlobalContext', async () => {
      expect(
        recordedEvents.withGlobalContext('PathContext').withGlobalContext('PathContext', 'http://localhost:3000/video')
          .events
      ).toStrictEqual([events[1], events[4], events[9]]);
    });
  });
});
