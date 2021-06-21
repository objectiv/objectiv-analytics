import { makeSectionContext } from '@objectiv/tracker-core';
import { render, screen } from '@testing-library/react';
import { renderHook } from '@testing-library/react-hooks';
import fetchMock from 'jest-fetch-mock';
import { ReactTracker, TrackerContextProvider, useTracker } from '../src';

describe('TrackerContextProvider', () => {
  beforeAll(() => {
    fetchMock.enableMocks();
  });

  it('should mount and render its children', () => {
    const reactTracker = new ReactTracker({ endpoint: '/collector' });
    render(
      <TrackerContextProvider tracker={reactTracker}>
        <div>First</div>
        <div>Second</div>
        <div>Third</div>
      </TrackerContextProvider>
    );

    screen.getByText(/First/);
    screen.getByText(/Second/);
    screen.getByText(/Third/);
  });

  describe('useTracker', () => {
    it('should throw an exception when called outside of TrackerContextProvider scope', () => {
      const hook = renderHook(() => useTracker());
      expect(hook.result.error).toStrictEqual(
        new Error('Objectiv: `useTracker` requires `TrackerContextProvider` to be present in the Components tree.')
      );
    });

    it('should retrieve the tracker from the closes Context Provider', () => {
      const endpoint = '/collector';
      const root = new ReactTracker({ endpoint, location_stack: [makeSectionContext({ id: 'root' })] });
      const section1 = new ReactTracker(root, { location_stack: [makeSectionContext({ id: 'section1' })] });
      const section2 = new ReactTracker(section1, { location_stack: [makeSectionContext({ id: 'section2' })] });

      const spy = jest.fn();

      const TrackingComponent = ({ id }: { id: string }) => {
        const tracker = useTracker();
        const location_stackAsPath = tracker.location_stack.map((locationContext) => locationContext.id).join('/');
        spy(`${id}: ${location_stackAsPath}`);
        return <div data-testid={id}>{location_stackAsPath}</div>;
      };

      render(
        <TrackerContextProvider tracker={root}>
          <div data-id={'tracker'}>
            <TrackingComponent id={'in-root'} />
            <TrackerContextProvider tracker={section1}>
              <TrackingComponent id={'in-section1'} />
              <TrackerContextProvider tracker={section2}>
                <TrackingComponent id={'in-section2'} />
              </TrackerContextProvider>
            </TrackerContextProvider>
          </div>
        </TrackerContextProvider>
      );

      expect(spy).toHaveBeenCalledTimes(3);
      expect(spy).toHaveBeenNthCalledWith(1, 'in-root: root');
      expect(spy).toHaveBeenNthCalledWith(2, 'in-section1: root/section1');
      expect(spy).toHaveBeenNthCalledWith(3, 'in-section2: root/section1/section2');
    });
  });
});
