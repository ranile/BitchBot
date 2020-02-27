import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowWarnComponent } from './show-warn.component';

describe('ShowWarnComponent', () => {
  let component: ShowWarnComponent;
  let fixture: ComponentFixture<ShowWarnComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowWarnComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowWarnComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
