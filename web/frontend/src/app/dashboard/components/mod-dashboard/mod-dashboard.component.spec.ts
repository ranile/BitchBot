import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModDashboardComponent } from './mod-dashboard.component';

describe('ModDashboardComponent', () => {
  let component: ModDashboardComponent;
  let fixture: ComponentFixture<ModDashboardComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModDashboardComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
