import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowAllRemindersComponent } from './show-all-reminders.component';

describe('ShowAllRemindersComponent', () => {
  let component: ShowAllRemindersComponent;
  let fixture: ComponentFixture<ShowAllRemindersComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowAllRemindersComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowAllRemindersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
