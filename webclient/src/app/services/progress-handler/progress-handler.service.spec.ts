import { TestBed } from '@angular/core/testing';

import { ProgressHandlerService } from './progress-handler.service';

describe('ProgressHandlerService', () => {
  let service: ProgressHandlerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProgressHandlerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
