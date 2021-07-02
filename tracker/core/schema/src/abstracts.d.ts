export abstract class AbstractEvent {
  location_stack?: AbstractLocationContext[];
  global_contexts?: AbstractGlobalContext[];
  event: string;
}
export abstract class AbstractContext {
  id: string;
  _context_type: string;
}
export abstract class AbstractLocationContext extends AbstractContext {
  readonly __location_context = true;
}
export abstract class AbstractGlobalContext extends AbstractContext {
  readonly __global_context = true;
}
export abstract class AbstractNonInteractiveEvent extends AbstractEvent {
  readonly __non_interactive_event = true;
}
export abstract class AbstractVideoEvent extends AbstractNonInteractiveEvent {
  readonly __video_event = true;
}
export abstract class AbstractInteractiveEvent extends AbstractEvent {
  readonly __interactive_event = true;
  location_stack: AbstractLocationContext[];
}
export abstract class AbstractSectionContext extends AbstractLocationContext {
  readonly __section_context = true;
}
export abstract class AbstractItemContext extends AbstractLocationContext {
  readonly __item_context = true;
}
export abstract class AbstractActionContext extends AbstractItemContext {
  readonly __action_context = true;
  path: string;
  text: string;
}
