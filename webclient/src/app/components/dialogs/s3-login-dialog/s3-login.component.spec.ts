import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { S3LoginComponent } from './s3-login.component';

describe('S3LoginComponent', () => {
  let component: S3LoginComponent;
  let fixture: ComponentFixture<S3LoginComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ S3LoginComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(S3LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
