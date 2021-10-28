import { generateUUID, makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { BrowserTracker, getTracker, makeTracker, tagButton, tagElement, TaggingAttribute } from '../src';
import { trackNewElements } from '../src/observer/trackNewElements';

describe('trackNewElements', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    makeTracker({ applicationId: generateUUID(), endpoint: 'test' });
    expect(getTracker()).toBeInstanceOf(BrowserTracker);
    jest.spyOn(getTracker(), 'trackEvent');
  });

  it('should apply tagging attributes to Elements tracked via Children Tracking and track them right away', async () => {
    const div1 = document.createElement('div');
    div1.setAttribute(
      TaggingAttribute.tagChildren,
      JSON.stringify([
        { queryAll: '#button', tagAs: tagButton({ id: 'button', text: 'button' }) },
        { queryAll: '#child-div', tagAs: tagElement({ id: 'child-div' }) },
      ])
    );

    const button = document.createElement('button');
    button.setAttribute('id', 'button');

    const childDiv = document.createElement('div');
    childDiv.setAttribute('id', 'child-div');

    jest.spyOn(div1, 'addEventListener');
    jest.spyOn(button, 'addEventListener');
    jest.spyOn(childDiv, 'addEventListener');

    div1.appendChild(button);
    div1.appendChild(childDiv);

    trackNewElements(div1, getTracker());

    expect(div1.addEventListener).not.toHaveBeenCalled();
    expect(childDiv.addEventListener).not.toHaveBeenCalled();
    expect(button.addEventListener).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenCalledTimes(1);
    expect(getTracker().trackEvent).toHaveBeenNthCalledWith(
      1,
      makeSectionVisibleEvent({
        location_stack: [
          expect.objectContaining({
            _type: 'SectionContext',
            id: 'child-div',
          }),
        ],
      })
    );
  });

  it('should console error', async () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});

    // @ts-ignore
    trackNewElements(null, getTracker());

    expect(getTracker().trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
