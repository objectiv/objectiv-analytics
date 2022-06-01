/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation } from '@objectiv/testing-tools';
import {
  LocationContextName,
  makeContentContext,
  makeLinkContext,
  makeNavigationContext,
  makePressableContext,
  makeRootLocationContext,
} from '@objectiv/tracker-core';
import { locationNodes, LocationTree, rootNode } from '../src/LocationTree';
import { TrackerConsole } from '../src/TrackerConsole';

TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocationTree', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  it('should not log anything (empty LocationTree)', () => {
    LocationTree.log();

    expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
  });

  it('should add nodes', () => {
    const root = makeRootLocationContext({ id: 'root' });
    const nav = makeNavigationContext({ id: 'nav' });
    const button = makePressableContext({ id: 'button' });
    const footer = makeNavigationContext({ id: 'footer' });

    expect(locationNodes).toHaveLength(1);

    LocationTree.add(root, null);
    LocationTree.add(nav, root);
    LocationTree.add(button, nav);
    LocationTree.add(footer, root);

    expect(locationNodes).toHaveLength(5);
    expect(locationNodes).toStrictEqual([
      expect.objectContaining({
        _type: 'LocationTreeRoot',
        id: 'location-tree-root',
      }),
      expect.objectContaining({
        __instance_id: root.__instance_id,
        _type: LocationContextName.RootLocationContext,
        id: 'root',
        parentLocationId: rootNode.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'nav',
        parentLocationId: root.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.PressableContext,
        id: 'button',
        parentLocationId: nav.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'footer',
        parentLocationId: root.__instance_id,
      }),
    ]);
  });

  it('should remove nodes', () => {
    const root = makeRootLocationContext({ id: 'root' });
    const nav = makeNavigationContext({ id: 'nav' });
    const button = makePressableContext({ id: 'button' });
    const footer = makeNavigationContext({ id: 'footer' });

    expect(locationNodes).toHaveLength(1);

    LocationTree.add(root, null);
    LocationTree.add(nav, root);
    LocationTree.add(button, nav);
    LocationTree.add(footer, root);

    expect(locationNodes).toHaveLength(5);

    LocationTree.remove(button);

    expect(locationNodes).toHaveLength(4);
    expect(locationNodes).toStrictEqual([
      expect.objectContaining({
        _type: 'LocationTreeRoot',
        id: 'location-tree-root',
      }),
      expect.objectContaining({
        __instance_id: root.__instance_id,
        _type: LocationContextName.RootLocationContext,
        id: 'root',
        parentLocationId: rootNode.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'nav',
        parentLocationId: root.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'footer',
        parentLocationId: root.__instance_id,
      }),
    ]);
  });

  it('should remove branches', () => {
    const root = makeRootLocationContext({ id: 'root' });
    const nav = makeNavigationContext({ id: 'nav' });
    const button = makePressableContext({ id: 'button' });
    const footer = makeNavigationContext({ id: 'footer' });

    expect(locationNodes).toHaveLength(1);

    LocationTree.add(root, null);
    LocationTree.add(nav, root);
    LocationTree.add(button, nav);
    LocationTree.add(footer, root);

    expect(locationNodes).toHaveLength(5);

    LocationTree.remove(nav);

    expect(locationNodes).toHaveLength(3);
    expect(locationNodes).toStrictEqual([
      expect.objectContaining({
        _type: 'LocationTreeRoot',
        id: 'location-tree-root',
      }),
      expect.objectContaining({
        __instance_id: root.__instance_id,
        _type: LocationContextName.RootLocationContext,
        id: 'root',
        parentLocationId: rootNode.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'footer',
        parentLocationId: root.__instance_id,
      }),
    ]);
  });

  it('should remove orphan nodes and branches', () => {
    const root = makeRootLocationContext({ id: 'root' });
    const nav = makeNavigationContext({ id: 'nav' });
    const button = makePressableContext({ id: 'button' });
    const main = makeContentContext({ id: 'main' });
    const hero = makeContentContext({ id: 'hero' });
    const link1 = makeLinkContext({ id: 'link', href: '/link1' });
    const link2 = makeLinkContext({ id: 'link', href: '/link2' });
    const footer = makeNavigationContext({ id: 'footer' });

    expect(locationNodes).toHaveLength(1);

    LocationTree.add(root, null);
    LocationTree.add(nav, root);
    LocationTree.add(button, nav);
    LocationTree.add(main, root);
    LocationTree.add(hero, main);
    LocationTree.add(link1, hero);
    LocationTree.add(footer, root);
    LocationTree.add(link2, footer);

    expect(locationNodes).toHaveLength(9);

    LocationTree.remove(footer);
    LocationTree.remove(main);

    expect(locationNodes).toHaveLength(4);
    expect(locationNodes).toStrictEqual([
      expect.objectContaining({
        _type: 'LocationTreeRoot',
        id: 'location-tree-root',
      }),
      expect.objectContaining({
        __instance_id: root.__instance_id,
        _type: LocationContextName.RootLocationContext,
        id: 'root',
        parentLocationId: rootNode.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.NavigationContext,
        id: 'nav',
        parentLocationId: root.__instance_id,
      }),
      expect.objectContaining({
        _type: LocationContextName.PressableContext,
        id: 'button',
        parentLocationId: nav.__instance_id,
      }),
    ]);
  });

  it('should TrackerConsole.error collisions', () => {
    const rootSection = makeContentContext({ id: 'root' });
    const section1 = makeContentContext({ id: '1' });
    const section2 = makeContentContext({ id: 'oops' });
    const section3 = makeContentContext({ id: 'oops' });
    const section4 = makeContentContext({ id: 'oops' });

    LocationTree.add(rootSection, null);
    LocationTree.add(section1, rootSection);
    LocationTree.add(section2, rootSection);
    LocationTree.add(section3, rootSection);
    LocationTree.add(section4, rootSection);

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv｣ Location collision detected: Content:root / Content:oops'
    );
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv｣ Location collision detected: Content:root / Content:oops'
    );
  });

  it('should not TrackerConsole.error collisions in children of already colliding nodes', () => {
    const rootSection = makeContentContext({ id: 'root' });
    const section1 = makeContentContext({ id: '1' });
    const section2 = makeContentContext({ id: 'oops' });
    const section3 = makeContentContext({ id: 'oops' });
    const section4 = makeContentContext({ id: '1' });
    const section5 = makeContentContext({ id: 'oops' });
    const section6 = makeContentContext({ id: 'oops' });

    LocationTree.add(rootSection, null);
    LocationTree.add(section1, rootSection);
    LocationTree.add(section2, rootSection);
    LocationTree.add(section3, rootSection);
    LocationTree.add(section4, rootSection);
    LocationTree.add(section5, section4);
    LocationTree.add(section6, section4);

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv｣ Location collision detected: Content:root / Content:oops'
    );
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv｣ Location collision detected: Content:root / Content:1'
    );
  });

  it('should log the Location tree', () => {
    const rootSection = makeContentContext({ id: 'root' });
    const section1 = makeContentContext({ id: '1' });
    const section2 = makeContentContext({ id: '2' });
    const section2a = makeContentContext({ id: '2a' });
    const section2b = makeContentContext({ id: '2b' });
    const section3 = makeContentContext({ id: '3' });
    const section3a = makeContentContext({ id: '3a' });
    const footer = makeContentContext({ id: 'footer' });
    const section4 = makeContentContext({ id: '4' });

    LocationTree.add(rootSection, null);
    LocationTree.add(section1, rootSection);
    LocationTree.add(section2, rootSection);
    LocationTree.add(section2a, section2);
    LocationTree.add(section2b, section2);
    LocationTree.add(section3, rootSection);
    LocationTree.add(section3a, section3);
    LocationTree.add(footer, rootSection);
    LocationTree.add(section4, footer);

    jest.resetAllMocks();

    LocationTree.log();

    expect(MockConsoleImplementation.log).toHaveBeenCalledTimes(9);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(1, `${LocationContextName.ContentContext}:root`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(2, `  ${LocationContextName.ContentContext}:1`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(3, `  ${LocationContextName.ContentContext}:2`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(4, `    ${LocationContextName.ContentContext}:2a`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(5, `    ${LocationContextName.ContentContext}:2b`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(6, `  ${LocationContextName.ContentContext}:3`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(7, `    ${LocationContextName.ContentContext}:3a`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(8, `  ${LocationContextName.ContentContext}:footer`);
    expect(MockConsoleImplementation.log).toHaveBeenNthCalledWith(9, `    ${LocationContextName.ContentContext}:4`);
  });
});
