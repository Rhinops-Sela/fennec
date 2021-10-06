import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BrowseStoredFilesComponent } from './browse-stored-files.component';

describe('BrowseStoredFilesComponent', () => {
  let component: BrowseStoredFilesComponent;
  let fixture: ComponentFixture<BrowseStoredFilesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BrowseStoredFilesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BrowseStoredFilesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
