/*
 * Copyright 2021 Objectiv B.V.
 */

import { WebDocumentContextPlugin } from '@objectiv/plugin-web-document-context';
import {
  generateUUID,
  getLocationPath,
  LocationStack,
  makeSectionContext,
  TrackerPlugins,
} from '@objectiv/tracker-core';
import { BrowserTracker, getElementLocationStack, TaggableElement } from '../src';
import { makeTaggedElement } from './mocks/makeTaggedElement';

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
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('errors', () => {
    it('should console.error when invoked with `null`', () => {
      // @ts-ignore
      expect(getElementLocationStack(null)).toHaveLength(0);
      expect(console.error).toHaveBeenCalledTimes(1);
    });
  });

  describe('Should reconstruct the Location Stack solely based on the DOM tree', () => {
    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'Section:main'],
      [div, 'Section:main'],
      [parentSection, 'Section:main / Section:parent'],
      [section, 'Section:main / Section:parent'],
      [childSection, 'Section:main / Section:parent / Section:child'],
      [button, 'Section:main / Section:parent / Section:child / Button:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element });
        const locationPath = getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });

  describe('Should reconstruct the Location Stack including the Plugins', () => {
    const applicationId = 'app';
    const endpoint = 'http://test';
    const plugins: TrackerPlugins = new TrackerPlugins({
      plugins: [new WebDocumentContextPlugin({ documentContextId: applicationId })],
    });
    const tracker = new BrowserTracker({ applicationId, endpoint, plugins });

    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'WebDocument:app / Section:main'],
      [div, 'WebDocument:app / Section:main'],
      [parentSection, 'WebDocument:app / Section:main / Section:parent'],
      [section, 'WebDocument:app / Section:main / Section:parent'],
      [childSection, 'WebDocument:app / Section:main / Section:parent / Section:child'],
      [button, 'WebDocument:app / Section:main / Section:parent / Section:child / Button:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element, tracker });
        const locationPath = getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });

  describe('Should reconstruct the Location Stack including the Tracker Location Stack and Plugins', () => {
    const applicationId = 'app';
    const endpoint = 'http://test';
    const location_stack: LocationStack = [makeSectionContext({ id: 'root' })];
    const plugins: TrackerPlugins = new TrackerPlugins({
      plugins: [new WebDocumentContextPlugin({ documentContextId: applicationId })],
    });
    const tracker = new BrowserTracker({ applicationId, endpoint, plugins, location_stack });

    const expectedPathsByElement: [TaggableElement, string][] = [
      [mainSection, 'WebDocument:app / Section:root / Section:main'],
      [div, 'WebDocument:app / Section:root / Section:main'],
      [parentSection, 'WebDocument:app / Section:root / Section:main / Section:parent'],
      [section, 'WebDocument:app / Section:root / Section:main / Section:parent'],
      [childSection, 'WebDocument:app / Section:root / Section:main / Section:parent / Section:child'],
      [button, 'WebDocument:app / Section:root / Section:main / Section:parent / Section:child / Button:button'],
    ];

    expectedPathsByElement.forEach(([element, expectedLocationPath]) => {
      it(`element: ${element.dataset.objectivElementId}: ${expectedLocationPath}`, () => {
        const locationStack = getElementLocationStack({ element, tracker });
        const locationPath = getLocationPath(locationStack);

        expect(locationPath).toBe(expectedLocationPath);
      });
    });
  });
});
