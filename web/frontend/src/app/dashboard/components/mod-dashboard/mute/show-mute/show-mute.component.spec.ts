import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowMuteComponent } from './show-mute.component';

describe('ShowMuteComponent', () => {
  let component: ShowMuteComponent;
  let fixture: ComponentFixture<ShowMuteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowMuteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowMuteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
