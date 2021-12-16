/*
 * Copyright 2021 Objectiv B.V.
 */

import { LocationTree, makeSectionContext } from '../src';

describe('LocationTree', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
    LocationTree.clear();
  });

  afterEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  it('should not log anything (empty LocationTree)', () => {
    LocationTree.log();

    expect(console.log).not.toHaveBeenCalled();
  });

  it('should not log anything (falsy input)', () => {
    // @ts-ignore
    LocationTree.log(0);

    expect(console.log).not.toHaveBeenCalled();
  });

  it('should throw if the given parentLocation does not exist', () => {
    // We create two Locations, but we do not add them to the LocationTree, thus parent retrieval will fail
    const location = makeSectionContext({ id: 'root' });
    const parentLocation = makeSectionContext({ id: 'parent' });

    expect(() => LocationTree.add(location, parentLocation)).toThrow('Parent LocationNode not found.');
  });

  it('should console.error collisions once', () => {
    const rootSection = makeSectionContext({ id: 'root' });
    const section1 = makeSectionContext({ id: '1' });
    const section2 = makeSectionContext({ id: 'oops' });
    const section3 = makeSectionContext({ id: 'oops' });
    const section4 = makeSectionContext({ id: 'oops' });

    LocationTree.add(rootSection);
    LocationTree.add(section1, rootSection);
    LocationTree.add(section2, rootSection);
    LocationTree.add(section3, rootSection);
    LocationTree.add(section4, rootSection);

    expect(console.error).toHaveBeenCalledTimes(1);
    expect(console.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv｣ Location collision detected: Section:root / Section:oops'
    );
  });

  it('should log the Location tree', () => {
    const rootSection = makeSectionContext({ id: 'root' });
    const section1 = makeSectionContext({ id: '1' });
    const section2 = makeSectionContext({ id: '2' });
    const section2a = makeSectionContext({ id: '2a' });
    const section2b = makeSectionContext({ id: '2b' });
    const section3 = makeSectionContext({ id: '3' });
    const section3a = makeSectionContext({ id: '3a' });

    LocationTree.add(rootSection);
    LocationTree.add(section1, rootSection);
    LocationTree.add(section2, rootSection);
    LocationTree.add(section2a, section2);
    LocationTree.add(section2b, section2);
    LocationTree.add(section3, rootSection);
    LocationTree.add(section3a, section3);

    jest.spyOn(console, 'log').mockImplementation(() => {});

    LocationTree.log();

    expect(console.log).toHaveBeenCalledTimes(7);
    expect(console.log).toHaveBeenNthCalledWith(1, '  SectionContext:root');
    expect(console.log).toHaveBeenNthCalledWith(2, '    SectionContext:1');
    expect(console.log).toHaveBeenNthCalledWith(3, '    SectionContext:2');
    expect(console.log).toHaveBeenNthCalledWith(4, '      SectionContext:2a');
    expect(console.log).toHaveBeenNthCalledWith(5, '      SectionContext:2b');
    expect(console.log).toHaveBeenNthCalledWith(6, '    SectionContext:3');
    expect(console.log).toHaveBeenNthCalledWith(7, '      SectionContext:3a');
  });
});
