import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowCommandComponent } from './show-command.component';

describe('ShowCommandComponent', () => {
  let component: ShowCommandComponent;
  let fixture: ComponentFixture<ShowCommandComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowCommandComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowCommandComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
