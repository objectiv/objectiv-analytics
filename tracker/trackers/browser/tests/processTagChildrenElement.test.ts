/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { makePressableContext } from '@objectiv/tracker-core';
import { isTaggedElement, processTagChildrenElement, tagContent, TaggingAttribute, tagPressable } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('processChildrenTrackingElement', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should exit with an empty array if the given Element has no children tagging attribute', () => {
    const div = document.createElement('div');

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should exit with an empty array if the given Element has an invalid children tagging attribute', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.tagChildren, 'null');

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should exit with an empty array if the given Element has an empty list of children tracking queries', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.tagChildren, '[]');

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should skip queries without tagAs', () => {
    const div = document.createElement('div');
    div.setAttribute(TaggingAttribute.tagChildren, JSON.stringify([{ queryAll: '#some-id-2', tagAs: null }]));

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should skip queries without valid or empty tagAs, query or queryAll options', () => {
    const div = document.createElement('div');
    div.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#some-id-1' },
        { queryAll: '#some-id-2', tagAs: null },
        { queryAll: '#some-id-3', tagAs: {} },
        { tagAs: tagContent({ id: 'element-id-1' }) },
        { queryAll: null, tagAs: tagContent({ id: 'element-id-2' }) },
        { queryAll: '', tagAs: tagContent({ id: 'element-id-3' }) },
      ])
    );

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should skip queries with failing querySelector expressions', () => {
    const div = document.createElement('div');
    div.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#button-id-1', tagAs: tagPressable({ id: 'button-id' }) },
        { queryAll: '[class="button"]', tagAs: tagPressable({ id: 'button-id' }) },
      ])
    );

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should match the first query', () => {
    const div = document.createElement('div');
    const childButton = document.createElement('button');
    childButton.setAttribute('id', 'button-id-1');
    div.appendChild(childButton);

    div.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#button-id-1', tagAs: tagPressable({ id: 'button-id' }) },
        { queryAll: '[class="button"]', tagAs: tagPressable({ id: 'button-id' }) },
      ])
    );

    const result = processTagChildrenElement(div);

    const expectedPressableContext = {
      ...makePressableContext({ id: 'button-id' }),
      __instance_id: matchUUID,
    };

    expect(result).toHaveLength(1);
    expect(isTaggedElement(result[0])).toBe(true);
    expect(JSON.parse(result[0].getAttribute(TaggingAttribute.context) ?? '')).toStrictEqual(expectedPressableContext);
  });
});
