import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ShowWarnsComponent } from './show-warns.component';

describe('ShowWarnsComponent', () => {
  let component: ShowWarnsComponent;
  let fixture: ComponentFixture<ShowWarnsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ShowWarnsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ShowWarnsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
