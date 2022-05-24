/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { PathContextFromURLPlugin } from '@objectiv/plugin-path-context-from-url';
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateUUID, LocationStack, makeContentContext, TrackerPluginInterface } from '@objectiv/tracker-core';
import { BrowserTracker, getElementLocationStack, TaggableElement } from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('getElementLocationStack', () => {
  const mainSection = makeTaggedElement(generateUUID(), 'main', 'section');
  const div = document.createElement('div');
  const parentSection = makeTaggedElement(generateUUID(), 'parent', 'div');
  const section = document.createElement('section');
  const childSection = makeTaggedElement(generateUUID(), 'child', 'span');
  const button = makeTaggedElement(generateUUID(), 'button', 'button', true);

  mainSection.appendChild(div);
  div.appendChild(parentSection);
  parentSection.appendChild(section);
  section.appendChild(childSection);
  childSection.appendChild(button);

  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe('errors', () => {
    it('should TrackerConsole.error when invoked with `null`', () => {
      // @ts-ignore
      expect(getElementLocationStack(null)).toHaveLength(0);
      expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    });
  });

  describe('Should reconstruct the Location Stack solely based on the DOM tree', () => {
    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'Content:main'],
      [div, 'Content:main'],
      [parentSection, 'Content:main / Content:parent'],
      [section, 'Content:main / Content:parent'],
      [childSection, 'Content:main / Content:parent / Content:child'],
      [button, 'Content:main / Content:parent / Content:child / Pressable:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element });
        const locationPath = globalThis.objectiv?.getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });

  describe('Should reconstruct the Location Stack including the Plugins', () => {
    const applicationId = 'app';
    const endpoint = 'http://test';
    const plugins: TrackerPluginInterface[] = [new PathContextFromURLPlugin()];
    const tracker = new BrowserTracker({ applicationId, endpoint, plugins });

    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'Content:main'],
      [div, 'Content:main'],
      [parentSection, 'Content:main / Content:parent'],
      [section, 'Content:main / Content:parent'],
      [childSection, 'Content:main / Content:parent / Content:child'],
      [button, 'Content:main / Content:parent / Content:child / Pressable:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element, tracker });
        const locationPath = globalThis.objectiv?.getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });

  describe('Should reconstruct the Location Stack including the Tracker Location Stack and Plugins', () => {
    const applicationId = 'app';
    const endpoint = 'http://test';
    const location_stack: LocationStack = [makeContentContext({ id: 'root' })];
    const plugins: TrackerPluginInterface[] = [new PathContextFromURLPlugin()];
    const tracker = new BrowserTracker({ applicationId, endpoint, plugins, location_stack });

    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'Content:root / Content:main'],
      [div, 'Content:root / Content:main'],
      [parentSection, 'Content:root / Content:main / Content:parent'],
      [section, 'Content:root / Content:main / Content:parent'],
      [childSection, 'Content:root / Content:main / Content:parent / Content:child'],
      [button, 'Content:root / Content:main / Content:parent / Content:child / Pressable:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element, tracker });
        const locationPath = globalThis.objectiv?.getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not TrackerConsole.error when invoked with `null`', () => {
      // @ts-ignore
      expect(getElementLocationStack(null)).toHaveLength(0);
      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });
  });
});
