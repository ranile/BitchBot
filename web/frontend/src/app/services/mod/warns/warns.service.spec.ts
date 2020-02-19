import { TestBed } from '@angular/core/testing';

import { WarnsService } from './warns.service';

describe('WarnsService', () => {
  let service: WarnsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(WarnsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
