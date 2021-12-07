/*
 * Copyright 2021 Objectiv B.V.
 */

import { makeButtonContext } from '@objectiv/tracker-core';
import { isTaggedElement, processTagChildrenElement, tagButton, tagElement, TaggingAttribute } from '../src';

describe('processChildrenTrackingElement', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
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
        { tagAs: tagElement({ id: 'element-id-1' }) },
        { queryAll: null, tagAs: tagElement({ id: 'element-id-2' }) },
        { queryAll: '', tagAs: tagElement({ id: 'element-id-3' }) },
      ])
    );

    expect(processTagChildrenElement(div)).toHaveLength(0);
  });

  it('should skip queries with failing querySelector expressions', () => {
    const div = document.createElement('div');
    div.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#button-id-1', tagAs: tagButton({ id: 'button-id', text: 'button' }) },
        { queryAll: '[class="button"]', tagAs: tagButton({ id: 'button-id', text: 'button' }) },
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
        { queryAll: '#button-id-1', tagAs: tagButton({ id: 'button-id', text: 'button' }) },
        { queryAll: '[class="button"]', tagAs: tagButton({ id: 'button-id', text: 'button' }) },
      ])
    );

    const result = processTagChildrenElement(div);

    const expectedButtonContext = makeButtonContext({ id: 'button-id', text: 'button' });

    expect(result).toHaveLength(1);
    expect(isTaggedElement(result[0])).toBe(true);
    expect(JSON.parse(result[0].getAttribute(TaggingAttribute.context) ?? '')).toStrictEqual(expectedButtonContext);
  });
});
