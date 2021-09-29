import { makeSectionVisibleEvent } from '@objectiv/tracker-core';
import { BrowserTracker, configureTracker, tagButton, tagElement, TaggingAttribute } from '../src';
import { trackNewElements } from '../src/observer/trackNewElements';

describe('trackNewElements', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    configureTracker({ applicationId: 'test', endpoint: 'test' });
    expect(window.objectiv.tracker).toBeInstanceOf(BrowserTracker);
    jest.spyOn(window.objectiv.tracker, 'trackEvent');
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

    trackNewElements(div1, window.objectiv.tracker);

    expect(div1.addEventListener).not.toHaveBeenCalled();
    expect(childDiv.addEventListener).not.toHaveBeenCalled();
    expect(button.addEventListener).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenCalledTimes(1);
    expect(window.objectiv.tracker.trackEvent).toHaveBeenNthCalledWith(
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
    jest.spyOn(console, 'error');

    // @ts-ignore
    trackNewElements(null, window.objectiv.tracker);

    expect(window.objectiv.tracker.trackEvent).not.toHaveBeenCalled();
    expect(console.error).toHaveBeenCalledTimes(1);
  });
});
