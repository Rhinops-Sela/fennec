import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DomainsLayoutComponent  } from './domains-layout.component';

describe('wizardComponent', () => {
  let component: DomainsLayoutComponent;
  let fixture: ComponentFixture<DomainsLayoutComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DomainsLayoutComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DomainsLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
