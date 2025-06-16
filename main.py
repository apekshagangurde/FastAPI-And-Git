from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select ,Relationship
from typing import Annotated,  List


app = FastAPI()

class Disease(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    patients: List["Patient"] = Relationship(back_populates="diseases", link_model="PatientDiseaseLink")

class PatientDiseaseLink(SQLModel, table=True):
    patient_id: int = Field(foreign_key="patient.id" ,primary_key=True)
    disease_id: int = Field(foreign_key="disease.id", primary_key=True)

class PatientBase(SQLModel):
    name: str = "Mr patient"
    age: int 
    disease: str |  None = None
    
class PatientPublic(PatientBase):
    pass
     
class PatientCreate(PatientBase):
    pass


class DoctorBase(SQLModel):
    name: str 
    age: int 
    Degree:str ="Dr"
    
class DoctorCreate(DoctorBase):
    pass   
    
class Doctor(DoctorBase,table=True):
    id: int | None = Field(default=None, primary_key=True)
    patients:List["Patient"] = Relationship(back_populates="doctor")
 
class Patient(PatientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    doctor_id: int | None = Field(default=None, foreign_key="doctor.id")
    doctor:"Doctor" = Relationship(back_populates="patients")
    diseases: List["Disease"] = Relationship(back_populates="patients", link_model=PatientDiseaseLink)
    

 
    
class DoctorPublic(DoctorBase):
    pass 
     
  
  

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/patients/", response_model=PatientPublic)
def create_patient(patient: PatientCreate, session: SessionDep):
    patient_obj = Patient(**patient.model_dump())
    session.add(patient_obj)
    session.commit()
    session.refresh(patient_obj)
    return patient

@app.post("/doctor/", response_model=DoctorPublic)
def create_doctor(doctor: DoctorCreate, session: SessionDep):
    doctor_obj = Doctor(**doctor.model_dump())
    session.add(doctor_obj )
    session.commit()
    session.refresh(doctor_obj)
    return doctor



@app.get("/patients/{patient_id}", response_model=Patient)
def read_patient(patient_id: int, session: SessionDep):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/patients/", response_model=List[Patient])
def read_all_patients(session: SessionDep):
    patients = session.exec(select(Patient))
    return patients


@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, updated_patient: Patient, session: SessionDep):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient.name = updated_patient.name
    patient.age = updated_patient.age
    patient.disease = updated_patient.disease
    
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, session: SessionDep):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    session.delete(patient)
    session.commit()
    return {"message": "Patient deleted successfully"}
