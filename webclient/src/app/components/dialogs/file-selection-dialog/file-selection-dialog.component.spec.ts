import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FileSelectionDialogComponent } from './file-selection-dialog.component';

describe('FileSelectionDialogComponent', () => {
  let component: FileSelectionDialogComponent;
  let fixture: ComponentFixture<FileSelectionDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FileSelectionDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FileSelectionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
