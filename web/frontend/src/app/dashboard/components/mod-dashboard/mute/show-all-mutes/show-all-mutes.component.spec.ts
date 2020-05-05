import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowAllMutesComponent } from './show-all-mutes.component';

describe('ShowAllMutesComponent', () => {
  let component: ShowAllMutesComponent;
  let fixture: ComponentFixture<ShowAllMutesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowAllMutesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowAllMutesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
