import { Directive, ElementRef, Input } from '@angular/core';
import {
  ChildrenTaggingQueries,
  tagButton,
  TagButtonParameters,
  tagChildren,
  TagChildrenReturnValue,
  tagElement,
  tagExpandableElement,
  tagInput,
  tagLink,
  TagLinkParameters,
  tagLocation,
  TagLocationHelperParameters,
  TagLocationParameters,
  TagLocationReturnValue,
  tagMediaPlayer,
  tagNavigation,
  tagOverlay,
} from '@objectiv/tracker-browser';

/**
 * Allows calling Browser Tracker Location Taggers and Children Taggers directly from templates
 */
@Directive({
  selector:
    '[tagLocation], [tagButton], [tagElement], [tagExpandableElement], [tagInput], [tagLink], [tagMediaPlayer], [tagNavigation], [tagOverlay], [tagChildren]',
})
export class ObjectivTrackerDirective {
  @Input() tagLocation: TagLocationParameters;
  @Input() tagButton: TagButtonParameters;
  @Input() tagElement: TagLocationHelperParameters;
  @Input() tagExpandableElement: TagLocationHelperParameters;
  @Input() tagInput: TagLocationHelperParameters;
  @Input() tagLink: TagLinkParameters;
  @Input() tagMediaPlayer: TagLocationHelperParameters;
  @Input() tagNavigation: TagLocationHelperParameters;
  @Input() tagOverlay: TagLocationHelperParameters;
  @Input() tagChildren: ChildrenTaggingQueries;

  constructor(public element: ElementRef<HTMLElement>) {}

  ngOnInit() {
    let locationTaggingAttributes: TagLocationReturnValue;
    let childrenTaggingAttributes: TagChildrenReturnValue;

    // Location Taggers
    if (this.tagLocation) {
      locationTaggingAttributes = tagLocation(this.tagLocation);
    } else if (this.tagButton) {
      locationTaggingAttributes = tagButton(this.tagButton);
    } else if (this.tagElement) {
      locationTaggingAttributes = tagElement(this.tagElement);
    } else if (this.tagExpandableElement) {
      locationTaggingAttributes = tagExpandableElement(this.tagExpandableElement);
    } else if (this.tagInput) {
      locationTaggingAttributes = tagInput(this.tagInput);
    } else if (this.tagLink) {
      locationTaggingAttributes = tagLink(this.tagLink);
    } else if (this.tagMediaPlayer) {
      locationTaggingAttributes = tagMediaPlayer(this.tagMediaPlayer);
    } else if (this.tagNavigation) {
      locationTaggingAttributes = tagNavigation(this.tagNavigation);
    } else if (this.tagOverlay) {
      locationTaggingAttributes = tagOverlay(this.tagOverlay);
    }

    // Children Tagger
    if (this.tagChildren) {
      childrenTaggingAttributes = tagChildren(this.tagChildren);
    }

    // Merge Location Tagging Attributes and Children Tagging Attributes
    const taggingAttributes = { ...(locationTaggingAttributes ?? {}), ...(childrenTaggingAttributes ?? {}) };

    // Set all attributes on the nativeElement
    for (let [key, value] of Object.entries<string>(taggingAttributes)) {
      this.element.nativeElement.setAttribute(key, value);
    }
  }
}
