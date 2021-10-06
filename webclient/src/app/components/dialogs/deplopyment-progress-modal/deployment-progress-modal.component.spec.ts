import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DeploymentProgressModalComponent } from './deployment-progress-modal.component';

describe('DeplopymentProgressComponent', () => {
  let component: DeploymentProgressModalComponent;
  let fixture: ComponentFixture<DeploymentProgressModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DeploymentProgressModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DeploymentProgressModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
