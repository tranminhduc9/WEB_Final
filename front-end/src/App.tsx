import Header from './components/Header';
import homePhoto from './assets/images/home_photo_1.png';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        {/* Hero Section với hình ảnh */}
        <section className="relative h-96 bg-gray-100 w-screen -mx-4">
          <img 
            src={homePhoto}
            alt="Du lịch Hà Nội" 
            className="w-full h-full object-cover"
          />
          
          <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
            
          </div>
        </section>
      </main>
    </div>
  );
}