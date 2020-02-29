import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowReminderComponent } from './show-reminder.component';

describe('ShowReminderComponent', () => {
  let component: ShowReminderComponent;
  let fixture: ComponentFixture<ShowReminderComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowReminderComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowReminderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
